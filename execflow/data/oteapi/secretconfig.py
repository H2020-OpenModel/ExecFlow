"""Authentication OTEAPI Config AiiDA Data Node class."""
from typing import TYPE_CHECKING

from oteapi.models import SecretConfig

from execflow.wrapper.data.base import ExtendedData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Optional, Union


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
        user: "Optional[str]" = None,
        password: "Optional[str]" = None,
        token: "Optional[str]" = None,
        client_id: "Optional[str]" = None,
        client_secret: "Optional[str]" = None,
        **kwargs: "Any",
    ) -> None:
        super().__init__(**kwargs)
        self.base.attributes.set_many(
            {
                "user": user
                or SecretConfig.schema()["properties"]["user"].get("default"),
                "password": password
                or SecretConfig.schema()["properties"]["password"].get("default"),
                "token": token
                or SecretConfig.schema()["properties"]["token"].get("default"),
                "client_id": client_id
                or SecretConfig.schema()["properties"]["client_id"].get("default"),
                "client_secret": client_secret
                or SecretConfig.schema()["properties"]["client_secret"].get("default"),
            }
        )

    @property
    def user(self) -> "Optional[str]":
        """User name for authentication."""
        return self.base.attributes.get("user")

    @user.setter
    def user(self, value: "Union[str, None]") -> None:
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
