from functools import reduce
import yaml
import requests
from typing import Callable, Dict, Optional, Tuple
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.middleware import csrf
from django.core.files.uploadedfile import SimpleUploadedFile

from saleor.account.models import User
from saleor.account.thumbnails import create_user_avatar_thumbnails
from saleor.graphql.core.utils import add_hash_to_file_name, validate_image_file
from saleor.core import jwt

from . import utils as u
from .external_auth_types import (
    Context,
    ExternalAccessTokens,
    ExternalAuthError,
    Provider,
    PluginConfigurationType,
    Uri,
)


def get_providers_from_config(
    configuration: PluginConfigurationType,
) -> Dict[str, Provider]:
    try:
        providers_config = configuration[0]["value"]
        return u.pipe(
            providers_config,
            yaml.safe_load,
            u.dict_keys_to_lower,
            u.instantiate(Uri),
            u.instantiate(Provider),
        )
    except (IndexError, TypeError):
        raise ExternalAuthError("No provider configuration available")


def get_context(providers: Dict[str, Provider]) -> Callable[[dict], Context]:
    """Get the authentication context merging the request payload
    and the selected provider from configuration"""

    def set_payload(payload: dict) -> Context:
        try:
            provider = providers.get(payload.get("provider").lower())
            if not provider:
                raise ExternalAuthError(f"Provider not found in configuration")
        except AttributeError:
            raise ExternalAuthError(f"Provider not found in configuration")

        return Context(payload=payload, provider=provider)

    return set_payload


def sanitize_secret(allowed_chars: str) -> Callable[[str], str]:
    """Let only allowed chars in secret string"""

    def inner(secret: str) -> str:
        return "".join(filter(lambda char: char in allowed_chars, str(secret)))

    return inner


def get_state(secret: str) -> str:
    """build state string from secret"""
    clean_secret = sanitize_secret(csrf.CSRF_ALLOWED_CHARS)(secret)
    return csrf._mask_cipher_secret(clean_secret)


def check_state(context: Context) -> Context:
    """Check if state string was made from provider's client_id"""

    secret = sanitize_secret(csrf.CSRF_ALLOWED_CHARS)(context.provider.client_id)
    state = context.payload.get("state")

    if not secret.startswith(csrf._unmask_cipher_token(state)):
        raise ExternalAuthError(f"Invalid request state")

    return context


def get_credentials(context: Context) -> Context:
    """Exchange with authentication provider the code received
    in the authetication url call for authentication tokens (credentials)"""

    provider = context.provider
    payload = context.payload

    try:
        data = {
            "code": payload.get("code"),
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "redirect_uri": payload.get("redirectUri", provider.redirect_uri),
            "grant_type": provider.tokens_uri.extra_params.get("grant_type"),
        }
        credentials = requests.post(provider.tokens_uri.path, data=data).json()
        if credentials.get("error"):
            raise ExternalAuthError(" ".join(credentials.values()))

        return Context(
            payload=payload,
            provider=provider,
            data={"credentials": credentials},
        )
    except requests.exceptions.RequestException:
        raise ExternalAuthError(
            f"Could not get credentials from {provider.provider_name} authorization server, check CLIENT_ID, CLIENT_SECRET, TOKENS_GRANT_TYPE and TOKENS_URI in Saleor Dashboard Plugin Config and that the authentication url is returning the CODE"
        )


def get_user_info(context: Context) -> Optional[dict]:
    """Use credentials to get user info like email, name, picture, etc."""

    provider = context.provider
    credentials = context.data.get("credentials")
    user_info_uri = u.make_uri(provider.user_info_uri.path)
    headers = {
        "Authorization": f"{credentials.get('token_type')} {credentials.get('access_token')}"
    }
    uri = user_info_uri(
        {
            "access_token": credentials.get("access_token"),
            **provider.user_info_uri.extra_params,
        }
    )
    user_info = requests.get(uri, headers=headers).json()

    if user_info.get("error"):
        raise ExternalAuthError(" ".join(user_info.values()))

    return user_info


def get_user(user_info: Optional[dict]) -> Optional[User]:
    """Get existing user from database or create a new one if not found.
    User with unverified emails are inactive until verification"""

    user, created = User.objects.get_or_create(
        email=user_info.get("email"),
        first_name=user_info.get("first_name", user_info.get("given_name")),
        last_name=user_info.get("last_name", user_info.get("family_name")),
    )

    get_user_pic = u.dict_str_lookup("http")
    user.avatar_uri = get_user_pic(user_info)
    return user


def update_avatar(user: User) -> User:
    response = requests.get(user.avatar_uri).json()
    if response.get("error"):
        raise ExternalAuthError(" ".join(response.values()))

    content_type = response.headers["Content-Type"]
    filename = (
        user.email.replace("@", "").replace(".", "") + "." + content_type.split("/")[1]
    )

    file = SimpleUploadedFile(
        content=response.content, name=filename, content_type=content_type
    )

    validate_image_file(file, "image", ValidationError)
    add_hash_to_file_name(file)
    if user.avatar:
        user.avatar.delete_sized_images()
        user.avatar.delete()
    user.avatar = file

    return user


def update_user(user: User) -> User:
    """Update existent user data with this login or
    create a new user if it's the first login"""

    user.last_login = timezone.now()
    update_fields = ["last_login"]

    if user.avatar_uri and not user.avatar:
        user = update_avatar(user)
        update_fields.append("avatar")

    if user.id:
        user.save(update_fields=update_fields)
    else:
        user.save()

    if "avatar" in update_fields:
        create_user_avatar_thumbnails.delay(user_id=user.pk)

    return user


def get_tokens(user: User) -> Tuple[User, ExternalAccessTokens]:
    """Get Saleor's Access Tokens with the user ID"""

    csrf_token = csrf._get_new_csrf_token()
    return ExternalAccessTokens(
        user=user,
        csrf_token=csrf_token,
        token=jwt.create_access_token(user),
        refresh_token=jwt.create_refresh_token(user, {"csrfToken": csrf_token}),
    )


# A pipe containing the sequence of funcions necessary to get tokens
tokens = u.pipe(
    check_state,
    get_credentials,
    get_user_info,
    get_user,
    update_user,
    get_tokens,
)
