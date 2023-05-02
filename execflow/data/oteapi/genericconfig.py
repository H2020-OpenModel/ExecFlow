"""Generic OTEAPI Config AiiDA Data Node class."""
from typing import TYPE_CHECKING

from execflow.wrapper.data.base import ExtendedData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


class GenericConfigData(ExtendedData):
    """Generic class for configuration objects.

    Args:
        configuration (dict): Model-specific configuration options,
            which can either be given as key/value-pairs or set as attributes.
        description (str): A description of the configuration model.

    """

    def __init__(
        self, configuration: "dict[str, Any]", description: str, **kwargs: "Any"
    ) -> None:
        super().__init__(**kwargs)

        attr_dict = {"configuration": configuration, "description": description}

        self.base.attributes.set_many(attr_dict)

    @property
    def configuration(self) -> "dict[str, Any]":
        """Model-specific configuration options, which can either be given as
        key/value-pairs or set as attributes."""
        return self.base.attributes.get("configuration")

    @configuration.setter
    def configuration(self, value: "dict[str, Any]") -> None:
        self.set_attribute("configuration", value)

    @property
    def description(self) -> str:
        """A description of the configuration model."""
        return self.base.attributes.get("description")

    @description.setter
    def description(self, value: str) -> None:
        self.set_attribute("description", value)
