"""AiiDA Process for the OTE Filter Strategy.

Since OTE Filter strategies may not subsequently invoke other AiiDA Workflows or
Calculations, it is semantically equivalent to an AiiDA Calculation.
"""
from typing import TYPE_CHECKING

from aiida.engine import calcfunction
from aiida.plugins import DataFactory
from oteapi.plugins import create_strategy, load_strategies

if TYPE_CHECKING:  # pragma: no cover
    from aiida.orm import Dict
    from oteapi.interfaces import IFilterStrategy

    from execflow.wrapper.data.filterconfig import FilterConfigData


@calcfunction
def init_filter(config: "FilterConfigData", session: "Dict") -> "Dict":
    """Initialize an OTE Filter strategy."""
    load_strategies()

    strategy: "IFilterStrategy" = create_strategy("filter", config.get_dict())
    updated_session = session.get_dict()
    updated_session.update(strategy.initialize(updated_session))
    return DataFactory("core.dict")(updated_session)


@calcfunction
def get_filter(config: "FilterConfigData", session: "Dict") -> "Dict":
    """Get/Execute an OTE Filter strategy."""
    load_strategies()

    strategy: "IFilterStrategy" = create_strategy("filter", config.get_dict())
    updated_session = session.get_dict()
    updated_session.update(strategy.get(updated_session))
    return DataFactory("core.dict")(updated_session)
