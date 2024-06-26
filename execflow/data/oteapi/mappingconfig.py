"""OTEAPI Mapping strategy config AiiDA Data Node class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oteapi.models import MappingConfig

from execflow.data.oteapi.genericconfig import GenericConfigData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    RDFTriple = tuple[str, str, str]


class MappingConfigData(GenericConfigData):
    """Mapping Strategy Data Configuration.

    Args:
        mappingType (str): Type of registered mapping strategy.
        prefixes (Optional[dict[str, str]]): List of shortnames that expands to an
            IRI given as local value/IRI-expansion-pairs.
        triples (Optional[list[RDFTriple]]): List of RDF triples given as (subject,
            predicate, object).

    """

    def __init__(
        self,
        mappingType: str,
        prefixes: dict[str, str] | None = None,
        triples: list[RDFTriple] | None = None,
        **kwargs: Any,
    ) -> None:
        if prefixes is None:
            prefixes = MappingConfig.model_fields["prefixes"].default

        if triples is None:
            triples = MappingConfig.model_fields["triples"].default

        super().__init__(**kwargs)

        attr_dict = {
            "mappingType": mappingType,
            "prefixes": prefixes,
            "triples": triples,
        }

        self.base.attributes.set_many(attr_dict)

    @property
    def mappingType(self) -> str:
        """Type of registered mapping strategy."""
        return self.base.attributes.get("mappingType")

    @mappingType.setter
    def mappingType(self, value: str) -> None:
        self.set_attribute("mappingType", value)

    @property
    def prefixes(self) -> dict[str, str] | None:
        """List of shortnames that expands to an IRI given as local
        value/IRI-expansion-pairs."""
        return self.base.attributes.get("prefixes")

    @prefixes.setter
    def prefixes(self, value: dict[str, str] | None) -> None:
        self.set_attribute("prefixes", value)

    @property
    def triples(self) -> RDFTriple | None:
        """List of RDF triples given as (subject, predicate, object)."""
        return self.base.attributes.get("triples")

    @triples.setter
    def triples(self, value: RDFTriple | None) -> None:
        self.set_attribute("triples", value)
