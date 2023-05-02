"""OTEAPI Filter strategy config AiiDA Data Node class."""
# pylint: disable=invalid-name
from typing import TYPE_CHECKING

from oteapi.models import FilterConfig

from execflow.wrapper.data.genericconfig import GenericConfigData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Optional, Union


class FilterConfigData(GenericConfigData):
    """Filter Strategy Data Configuration.

    Args:
        filterType (str): Type of registered filter strategy. E.g., `filter/sql`.
        query (Optional[str]): Define a query operation.
        condition (Optional[str]): Logical statement indicating when a filter should be
            applied.
        limit (Optional[int]): Number of items remaining after a filter expression.

    """

    def __init__(
        self,
        filterType: str,
        query: "Optional[str]" = None,
        condition: "Optional[str]" = None,
        limit: "Optional[int]" = None,
        **kwargs: "Any",
    ) -> None:
        if query is None:
            query = FilterConfig.schema()["properties"]["query"].get("default")

        if condition is None:
            condition = FilterConfig.schema()["properties"]["condition"].get("default")

        if limit is None:
            limit = FilterConfig.schema()["properties"]["limit"].get("default")

        super().__init__(**kwargs)

        attr_dict = {
            "filterType": filterType,
            "query": query,
            "condition": condition,
            "limit": limit,
        }

        self.base.attributes.set_many(attr_dict)

    @property
    def filterType(self) -> str:
        """Type of registered filter strategy. E.g., `filter/sql`."""
        return self.base.attributes.get("filterType")

    @filterType.setter
    def filterType(self, value: str) -> None:
        self.set_attribute("filterType", value)

    @property
    def query(self) -> "Union[str, None]":
        """Define a query operation."""
        return self.base.attributes.get("query")

    @query.setter
    def query(self, value: "Union[str, None]") -> None:
        self.set_attribute("query", value)

    @property
    def condition(self) -> "Union[str, None]":
        """Logical statement indicating when a filter should be applied."""
        return self.base.attributes.get("condition")

    @condition.setter
    def condition(self, value: "Union[str, None]") -> None:
        self.set_attribute("condition", value)

    @property
    def limit(self) -> "Union[int, None]":
        """Number of items remaining after a filter expression."""
        return self.base.attributes.get("limit")

    @limit.setter
    def limit(self, value: "Union[int, None]") -> None:
        self.set_attribute("limit", value)
