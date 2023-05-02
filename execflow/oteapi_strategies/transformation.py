"""AiiDA Processes for the OTE Transformation Strategy.

Since OTE Transformation strategies may subsequently invoke other AiiDA Workflows or
Calculations, it is semantically equivalent to an AiiDA Workflow.
"""
from time import sleep, time
from typing import TYPE_CHECKING

from aiida.engine import workfunction
from aiida.plugins import CalculationFactory, DataFactory
from oteapi.plugins import create_strategy, load_strategies

if TYPE_CHECKING:  # pragma: no cover
    from aiida.orm import Dict
    from oteapi.interfaces import ITransformationStrategy
    from oteapi.models import TransformationStatus

    from execflow.wrapper.data.transformationconfig import TransformationConfigData


@workfunction
def init_transformation(config: "TransformationConfigData", session: "Dict") -> "Dict":
    """Initialize an OTE Transformation strategy."""
    load_strategies()

    strategy: "ITransformationStrategy" = create_strategy(
        "transformation", config.get_dict()
    )
    updates_for_session = strategy.initialize(session.get_dict())

    return CalculationFactory("execflow.update_session")(
        session=session,
        updates=DataFactory("core.dict")(updates_for_session),
    )


@workfunction
def get_transformation(config: "TransformationConfigData", session: "Dict") -> "Dict":
    """Get an OTE Transformation strategy.

    Important:
        Currently, the status values are valid only for Celery.

        This is because only a single transformation strategy exists (for Celery) and
        the configuration and status models have been based on this strategy.

        A status enumeration should be set as the type for
        `TransformationStatus.status` in order to more agnostically determine the state
        from any transformation strategy.

        However, this is to be implemented in OTEAPI Core.

    """
    load_strategies()

    strategy: "ITransformationStrategy" = create_strategy(
        "transformation", config.get_dict()
    )

    wall_time = 2 * 60  # 2 min.

    start_time = time()
    status: "TransformationStatus" = strategy.run(session.get_dict())
    while (
        status.status
        not in (
            "READY_STATES",
            "EXCEPTION_STATES",
            "PROPAGATE_STATES",
            "SUCCESS",
            "FAILURE",
            "REVOKED",
            "RETRY",
        )
        or not status.finishTime
    ) and (time() - start_time) < wall_time:
        sleep(0.5)
        status = strategy.status(status.id)

    updates_for_session = strategy.get(session.get_dict())

    return CalculationFactory("execflow.update_session")(
        session=session,
        updates=DataFactory("core.dict")(updates_for_session),
    )
