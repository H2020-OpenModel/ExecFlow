"""Base for all ExecFlow Data classes.

This contains an "extended" Data class, which is equivalent to aiida.orm.Data,
but has some extra methods or functionalities that is useful for the ExecFlow Data
classes.
"""
from typing import TYPE_CHECKING

from aiida.common.exceptions import ModificationNotAllowed
from aiida.orm import Data

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict


class ExtendedData(Data):
    """Equivalent to aiida.orm.Data but with extended functionality."""

    def set_attribute(self, attribute_name: str, value: "Any") -> None:
        """Set an attribute, ensuring the Node is not yet stored.

        Args:
            attribute_name: The name of the attribute to set.
            value: The value of the attribute.

        """
        if self.is_stored:
            raise ModificationNotAllowed(
                f"The {self.__class__.__name__} object cannot be modified, "
                "it has already been stored."
            )

        self.base.attributes.set(attribute_name, value)

    def get_dict(self) -> "Dict[str, Any]":
        """Return all attributes as a Python dictionary."""
        return dict(self.base.attributes.all)
