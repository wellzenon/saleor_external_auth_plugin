from typing import TYPE_CHECKING, Optional

from django.core.handlers.wsgi import WSGIRequest
from saleor.plugins.base_plugin import BasePlugin

from . import constants, utils
from . import external_auth as ea

from .external_auth_types import (
    ConfigurationTypeField,
    ExternalAccessTokens,
    PluginConfigurationType,
)

if TYPE_CHECKING:
    # flake8: noqa
    from channel.models import Channel


class SocialLoginPlugin(BasePlugin):
    """Abstract class for storing all methods available for any plugin.

    All methods take previous_value parameter.
    previous_value contains a value calculated by the previous plugin in the queue.
    If the plugin is first, it will use default value calculated by the manager.
    """

    PLUGIN_NAME = "Social Authentication Plugin"
    PLUGIN_ID = "plugin.socialauth"
    PLUGIN_DESCRIPTION = "A plugin for social authentication"
    CONFIG_STRUCTURE = {
        constants.CONFIGURATION_FIELD: {
            "type": ConfigurationTypeField.MULTILINE,
            "help_text": "Provide all necessary configuration for each provider",
            "label": "Providers Configuration List",
        }
    }
    CONFIGURATION_PER_CHANNEL = False
    DEFAULT_CONFIGURATION = [
        {
            "name": constants.CONFIGURATION_FIELD,
            "value": constants.DEFAULT_CONFIGURATION_TEXT,
        }
    ]
    DEFAULT_ACTIVE = False

    @classmethod
    def check_plugin_id(cls, plugin_id: str) -> bool:
        """Check if given plugin_id matches with the PLUGIN_ID of this plugin."""
        return cls.PLUGIN_ID == plugin_id

    def __init__(
        self,
        *,
        configuration: PluginConfigurationType,
        active: bool,
        channel: Optional["Channel"] = None,
    ):
        self.configuration = self.get_plugin_configuration(configuration)
        self.providers_config = ea.get_providers_from_config(self.configuration)
        self.active = active
        self.channel = channel

    def __str__(self):
        return self.PLUGIN_NAME

    def external_authentication_url(
        self, payload: dict, request: WSGIRequest, **kwargs
    ) -> dict:
        context = ea.get_context(self.providers_config)(payload)
        provider = context.provider
        auth_uri = utils.make_uri(provider.auth_uri.path)

        return {
            "authorizationUrl": auth_uri(
                {
                    "client_id": provider.client_id,
                    "state": ea.get_state(provider.client_id),
                    "redirect_uri": payload.get("redirectUri", provider.redirect_uri),
                    **provider.auth_uri.extra_params,
                }
            )
        }

    def external_obtain_access_tokens(
        self, payload: dict, request: WSGIRequest, previous_value: ExternalAccessTokens
    ) -> ExternalAccessTokens:
        context = ea.get_context(self.providers_config)(payload)
        tokens = ea.tokens(context)

        request._cached_user = tokens.user
        request.refresh_token = tokens.refresh_token

        return tokens
