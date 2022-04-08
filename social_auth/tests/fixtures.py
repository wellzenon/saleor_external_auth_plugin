import pytest
from ..external_auth_types import Context, Provider, User

providers_dict = {
    "google": Provider(
        provider_name="google",
        client_id="your google id",
        client_secret="your google secret",
        redirect_uri="http://localhost:3000/auth/google",
        auth_uri="https://accounts.google.com/o/oauth2/v2/auth",
        auth_scope="openid email profile",
        auth_accesss_type="offline",
        auth_include_granted_scopes="true",
        auth_response_type="code",
        tokens_uri="https://oauth2.googleapis.com/token",
        tokens_grant_type="authorization_code",
        user_info_uri="https://www.googleapis.com/oauth2/v2/userinfo",
    ),
    "facebook": Provider(
        provider_name="facebook",
        client_id="your facebook id",
        client_secret="your facebook secret",
        redirect_uri="http://localhost:300...uth/facebook",
        auth_uri="https://www.facebook.com/v13.0/dialog/oauth",
        auth_accesss_type="offline",
        auth_include_granted_scopes="true",
        auth_response_type="code",
        tokens_uri="https://graph.facebook.com/v13.0/oauth/access_token",
        tokens_grant_type="authorization_code",
        user_info_uri="https://graph.facebook.com/v13.0/me?fields=id,name,email,first_name,last_name,middle_name,is_guest_user,picture{url,height,width}",
    ),
}


@pytest.fixture
def config():
    return [
        {
            "name": "providers_config_list",
            "type": "Multiline",
            "label": "Providers Configuration List",
            "help_text": "Provide all necessar...h provider",
            "value": '{\n    "GOOGLE": \n        {\n            "PROVIDER_NAME":"google",\n            "CLIENT_ID": "your google id",\n            "CLIENT_SECRET": "your google secret",\n            "REDIRECT_URI": "http://localhost:3000/auth/google",\n            "AUTH_URI": "https://accounts.google.com/o/oauth2/v2/auth",\n            "AUTH_SCOPE": "openid email profile",\n            "AUTH_ACCESSS_TYPE": "offline",\n            "AUTH_INCLUDE_GRANTED_SCOPES": "true",\n            "AUTH_RESPONSE_TYPE": "code",\n            "TOKENS_URI": "https://oauth2.googleapis.com/token",\n            "TOKENS_GRANT_TYPE": "authorization_code",\n            "USER_INFO_URI": "https://www.googleapis.com/oauth2/v2/userinfo"\n        },\n    "FACEBOOK":\n        {\n            "PROVIDER_NAME":"facebook",\n            "CLIENT_ID": "your facebook id",\n            "CLIENT_SECRET": "your facebook secret",\n            "REDIRECT_URI": "http://localhost:3000/auth/facebook",\n            "AUTH_URI": "https://www.facebook.com/v13.0/dialog/oauth",\n            "AUTH_ACCESSS_TYPE": "offline",\n            "AUTH_INCLUDE_GRANTED_SCOPES": "true",\n            "AUTH_RESPONSE_TYPE": "code",\n            "TOKENS_URI": "https://graph.facebook.com/v13.0/oauth/access_token",\n            "TOKENS_GRANT_TYPE": "authorization_code",\n            "USER_INFO_URI": "https://graph.facebook.com/v13.0/me?fields=id,name,email,first_name,last_name,middle_name,is_guest_user,picture{url,height,width}"\n        }\n}',
        }
    ]


@pytest.fixture
def providers():
    return providers_dict


@pytest.fixture
def context():
    return Context(
        payload={
            "code": "98374089324jdfoq",
            "redirectUri": "http://localhost:3000/auth/google",
        },
        provider=providers_dict.get("google"),
    )


@pytest.fixture
def credentials():
    return {"token_type": "JWT", "access_token": "ioaUSHDAHwe9238hidnfiqh2wr89o"}


@pytest.fixture
def context_with_credentials():
    return Context(
        payload={
            "code": "98374089324jdfoq",
            "redirectUri": "http://localhost:3000/auth/google",
        },
        provider=providers_dict.get("google"),
        data={
            "credentials": {
                "token_type": "JWT",
                "access_token": "ioaUSHDAHwe9238hidnfiqh2wr89o",
            }
        },
    )


@pytest.fixture
def userinfo():
    return {
        "email": "john@doe.com",
        "given_name": "John",
        "family_name": "Doe",
        "picture": "http://somesite.com/pic.jpg",
        "verified_email": True,
    }


@pytest.fixture
def user():
    user = User(
        email="john@doe.com",
        first_name="John",
        last_name="Doe",
        is_active=True,
    )
    user.avatar_uri = "http://somesite.com/pic.jpg"

    return user
