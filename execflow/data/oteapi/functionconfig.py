"""OTEAPI Function strategy config AiiDA Data Node class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from execflow.data.oteapi.genericconfig import GenericConfigData
from execflow.data.oteapi.secretconfig import SecretConfigData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


class FunctionConfigData(GenericConfigData, SecretConfigData):
    """Function Strategy Data Configuration.

    Args:
        functionType (str): Type of registered function strategy.

    """

    def __init__(self, functionType: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.base.attributes.set("functionType", functionType)

    @property
    def functionType(self) -> str:
        """Type of registered function strategy."""
        return self.base.attributes.get("functionType")

    @functionType.setter
    def functionType(self, value: str) -> None:
        self.set_attribute("functionType", value)
