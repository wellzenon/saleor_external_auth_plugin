from django.http import HttpResponse
import pytest
from .. import external_auth as ea
from ..external_auth_types import Context, ExternalAuthError
from .fixtures import (
    config,
    providers,
    credentials,
    context,
    context_with_credentials,
    userinfo,
    user,
    providers_dict,
)

"""
To run only this plugin tests run:

pytest --pyargs social_auth --ds=saleor.settings -p no:django_queries -p no:faker -p no:forked -p no:celery -p no:mock -p no:cov
"""


def test_get_providers_from_config_when_config_is_empty():
    with pytest.raises(ExternalAuthError):
        ea.get_providers_from_config("")


def test_get_providers_from_config(config):
    assert ea.get_providers_from_config(config)


@pytest.mark.parametrize("input", ["", {"redirect": "http"}, {"provider": "github"}])
def test_get_context_with_empty_provider(providers, input):
    with pytest.raises(ExternalAuthError):
        ea.get_context(providers)(input)


def test_get_context(providers):
    assert ea.get_context(providers)({"provider": "google"})


def test_get_credentials(monkeypatch, context):
    json = {"token_type": "JWT", "access_token": "ioaUSHDAHwe9238hidnfiqh2wr89o"}

    def mocked_post(uri, *args, **kwargs):
        return type("MockedReq", (), {"json": lambda *x, **y: json})()

    monkeypatch.setattr(ea.get_credentials.__globals__["requests"], "post", mocked_post)
    assert ea.get_credentials(context) == Context(
        data={"credentials": json},
        payload={
            "code": "98374089324jdfoq",
            "redirectUri": "http://localhost:3000/auth/google",
        },
        provider=providers_dict.get("google"),
    )


def test_get_credentials_when_invalid_request(monkeypatch, context):
    with pytest.raises(ExternalAuthError):

        def mocked_post(uri, *args, **kwargs):
            json = {
                "error": "unsupported_grant_type",
                "error_description": "Invalid grant_type: ",
            }
            return type("MockedReq", (), {"json": lambda *x, **y: json})()

        monkeypatch.setattr(
            ea.get_credentials.__globals__["requests"], "post", mocked_post
        )
        ea.get_credentials(context)


def test_get_userinfo(monkeypatch, context_with_credentials):
    json = {
        "email": "john@doe.com",
        "given_name": "John",
        "family_name": "Doe",
        "picture": "http://somesite.com/pic.jpg",
    }

    def mocked_get(uri, *args, **kwargs):
        return type("MockedReq", (), {"json": lambda *x, **y: json})()

    monkeypatch.setattr(ea.get_userinfo.__globals__["requests"], "get", mocked_get)
    assert ea.get_userinfo(context_with_credentials) == json


def test_get_userinfo_with_invalid_request(monkeypatch, context_with_credentials):
    with pytest.raises(ExternalAuthError):
        json = {
            "error": "unsupported_grant_type",
            "error_description": "Invalid grant_type: ",
        }

        def mocked_get(uri, *args, **kwargs):
            return type("MockedReq", (), {"json": lambda *x, **y: json})()

        monkeypatch.setattr(ea.get_userinfo.__globals__["requests"], "get", mocked_get)
        ea.get_userinfo(context_with_credentials)


def test_get_user(userinfo):
    user = ea.get_user(userinfo)

    assert (
        user.email == "john@doe.com"
        and user.avatar_uri == "http://somesite.com/pic.jpg"
    )


@pytest.mark.django_db
def test_update_user(monkeypatch, user):
    json = HttpResponse(b"image", headers={"Content-Type": "image/jpeg"})
    filename = user.email.replace("@", "").replace(".", "")

    def mocked_get(uri, *args, **kwargs):
        return type("MockedReq", (), {"json": lambda *x, **y: json})()

    monkeypatch.setattr(ea.update_user.__globals__["requests"], "get", mocked_get)
    user = ea.update_user(user)

    assert (
        user.email == "john@doe.com"
        and user.is_active == True
        and filename in user.avatar.name
    )


# def test_get_tokens(context):
#     ...
