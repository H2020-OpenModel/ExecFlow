"""AiiDA Processes for the OTE Mapping Strategy.

Since OTE Mapping strategies may not subsequently invoke other AiiDA Workflows or
Calculations, it is semantically equivalent to an AiiDA Calculation.
"""
from typing import TYPE_CHECKING

from aiida.engine import calcfunction
from aiida.plugins import DataFactory
from oteapi.plugins import create_strategy, load_strategies

if TYPE_CHECKING:  # pragma: no cover
    from aiida.orm import Dict
    from oteapi.interfaces import IMappingStrategy

    from execflow.wrapper.data.mappingconfig import MappingConfigData


@calcfunction
def init_mapping(config: "MappingConfigData", session: "Dict") -> "Dict":
    """Initialize an OTE Mapping strategy."""
    load_strategies()

    strategy: "IMappingStrategy" = create_strategy("mapping", config.get_dict())
    updated_session = session.get_dict()
    updated_session.update(strategy.initialize(updated_session))
    return DataFactory("core.dict")(updated_session)


@calcfunction
def get_mapping(config: "MappingConfigData", session: "Dict") -> "Dict":
    """Get/Execute an OTE Mapping strategy."""
    load_strategies()

    strategy: "IMappingStrategy" = create_strategy("mapping", config.get_dict())
    updated_session = session.get_dict()
    updated_session.update(strategy.get(updated_session))
    return DataFactory("core.dict")(updated_session)
