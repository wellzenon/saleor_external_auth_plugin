from dataclasses import dataclass, field
from typing import Dict, List, Optional

from saleor.account.models import User

PluginConfigurationType = List[dict]
NoneType = type(None)


class ConfigurationTypeField:
    STRING = "String"
    MULTILINE = "Multiline"
    BOOLEAN = "Boolean"
    SECRET = "Secret"
    SECRET_MULTILINE = "SecretMultiline"
    PASSWORD = "Password"
    OUTPUT = "OUTPUT"
    CHOICES = [
        (STRING, "Field is a String"),
        (MULTILINE, "Field is a Multiline"),
        (BOOLEAN, "Field is a Boolean"),
        (SECRET, "Field is a Secret"),
        (PASSWORD, "Field is a Password"),
        (SECRET_MULTILINE, "Field is a Secret multiline"),
        (OUTPUT, "Field is a read only"),
    ]


@dataclass
class ExternalAccessTokens:
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    csrf_token: Optional[str] = None
    user: Optional["User"] = None


@dataclass
class Uri:
    path: str
    extra_params: Optional[Dict[str, str]] = field(default_factory=(lambda: {}))


@dataclass
class Provider:
    name: str
    client_id: str
    tokens_uri: Uri
    user_info_uri: Uri
    auth_uri: Optional[Uri] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None


@dataclass
class Context:
    payload: dict
    provider: Provider
    data: Optional[dict] = None


class ExternalAuthError(Exception):
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"External Authentication Error: {self.value}"


class AuthWarning(Warning):
    pass
