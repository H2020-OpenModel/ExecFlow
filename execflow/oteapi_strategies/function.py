"""AiiDA Process for the OTE Function Strategy.

Since OTE Function strategies may subsequently invoke other AiiDA Workflows or
Calculations, it is semantically equivalent to an AiiDA Workflow.
"""
from typing import TYPE_CHECKING

from aiida.engine import workfunction
from aiida.plugins import CalculationFactory, DataFactory
from oteapi.plugins import create_strategy, load_strategies

if TYPE_CHECKING:  # pragma: no cover
    from aiida.orm import Dict
    from oteapi.interfaces import IFunctionStrategy

    from execflow.data.oteapi.functionconfig import FunctionConfigData


@workfunction
def init_function(config: "FunctionConfigData", session: "Dict") -> "Dict":
    """Initialize an OTE Function strategy."""
    load_strategies(False)

    strategy: "IFunctionStrategy" = create_strategy("function", config.get_dict())
    updates_for_session = strategy.initialize(session.get_dict())

    return CalculationFactory("execflow.update_oteapi_session")(
        session=session,
        updates=DataFactory("core.dict")(updates_for_session),
    )


@workfunction
def get_function(config: "FunctionConfigData", session: "Dict") -> "Dict":
    """Get/Execute an OTE Function strategy."""
    load_strategies(False)

    strategy: "IFunctionStrategy" = create_strategy("function", config.get_dict())
    updates_for_session = strategy.get(session.get_dict())

    return CalculationFactory("execflow.update_oteapi_session")(
        session=session,
        updates=DataFactory("core.dict")(updates_for_session),
    )
