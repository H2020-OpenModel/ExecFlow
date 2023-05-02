"""OTEAPI Function strategy config AiiDA Data Node class."""
# pylint: disable=invalid-name
from typing import TYPE_CHECKING

from execflow.wrapper.data.genericconfig import GenericConfigData
from execflow.wrapper.data.secretconfig import SecretConfigData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


class FunctionConfigData(GenericConfigData, SecretConfigData):
    """Function Strategy Data Configuration.

    Args:
        functionType (str): Type of registered function strategy.

    """

    def __init__(self, functionType: str, **kwargs: "Any") -> None:
        super().__init__(**kwargs)

        self.base.attributes.set("functionType", functionType)

    @property
    def functionType(self) -> str:
        """Type of registered function strategy."""
        return self.base.attributes.get("functionType")

    @functionType.setter
    def functionType(self, value: str) -> None:
        self.set_attribute("functionType", value)
