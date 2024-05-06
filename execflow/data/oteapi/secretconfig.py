"""Authentication OTEAPI Config AiiDA Data Node class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oteapi.models import SecretConfig

from execflow.data.oteapi.base import ExtendedData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


class SecretConfigData(ExtendedData):
    """Extra configuration for authentication.

    Args:
        user (str): User name for authentication.
        password (str): Password for authentication.
        token (str): An access token for providing access and meta data to an
            application.
        client_id (str): Client ID for an OAUTH2 client.
        client_secret (str): Client secret for an OAUTH2 client.

    """

    def __init__(
        self,
        user: str | None = None,
        password: str | None = None,
        token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.base.attributes.set_many(
            {
                "user": user or SecretConfig.model_fields["user"].default,
                "password": password or SecretConfig.model_fields["password"].default,
                "token": token or SecretConfig.model_fields["token"].default,
                "client_id": client_id or SecretConfig.model_fields["client_id"].default,
                "client_secret": client_secret or SecretConfig.model_fields["client_secret"].default,
            }
        )

    @property
    def user(self) -> str | None:
        """User name for authentication."""
        return self.base.attributes.get("user")

    @user.setter
    def user(self, value: str | None) -> None:
        self.set_attribute("user", value)

    @property
    def password(self) -> str:
        """Password for authentication."""
        return self.base.attributes.get("password")

    @password.setter
    def password(self, value: str) -> None:
        self.set_attribute("password", value)

    @property
    def token(self) -> str:
        """An access token for providing access and meta data to an application."""
        return self.base.attributes.get("token")

    @token.setter
    def token(self, value: str) -> None:
        self.set_attribute("token", value)

    @property
    def client_id(self) -> str:
        """Client ID for an OAUTH2 client."""
        return self.base.attributes.get("client_id")

    @client_id.setter
    def client_id(self, value: str) -> None:
        self.set_attribute("client_id", value)

    @property
    def client_secret(self) -> str:
        """Client secret for an OAUTH2 client."""
        return self.base.attributes.get("client_secret")

    @client_secret.setter
    def client_secret(self, value: str) -> None:
        self.set_attribute("client_secret", value)
