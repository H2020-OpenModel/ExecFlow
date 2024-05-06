"""AiiDA calculation function for parsing a declarative pipeline."""

from pathlib import Path
from typing import TYPE_CHECKING

from aiida.common.exceptions import InputValidationError, ValidationError
from aiida.engine import calcfunction
from aiida.plugins import DataFactory

if TYPE_CHECKING:  # pragma: no cover
    from typing import Dict, Type, Union

    from aiida import orm

    from execflow.data.oteapi.declarative_pipeline import OTEPipelineData as ExecFlowOTEPipelineData
    from execflow.data.oteapi.genericconfig import GenericConfigData


@calcfunction
def parse_oteapi_pipeline(
    pipeline_input: "Union[ExecFlowOTEPipelineData, orm.Dict, orm.SinglefileData, orm.Str]",
) -> "Dict[str, Union[ExecFlowOTEPipelineData, Dict[str, GenericConfigData]]]":
    """Calculation function for parsing a declarative pipeline.

    Parameters:
        pipeline_input: The declarative pipeline.

    Returns:
        A dictionary of the parsed pipeline and a dict of OTE strategy configurations as
        AiiDA Data Nodes.

    """
    AiiDADict: "Type[orm.Dict]" = DataFactory("core.dict")
    AiiDAStr: "Type[orm.Str]" = DataFactory("core.str")
    OTEPipelineData: "Type[ExecFlowOTEPipelineData]" = DataFactory("execflow.oteapi_pipeline")
    SinglefileData: "Type[orm.SinglefileData]" = DataFactory("core.singlefile")

    if isinstance(pipeline_input, (OTEPipelineData, AiiDADict)):
        pipeline = OTEPipelineData(value=pipeline_input)
    elif isinstance(pipeline_input, SinglefileData):
        pipeline = OTEPipelineData(single_file=pipeline_input)
    elif isinstance(pipeline_input, AiiDAStr):
        if Path(pipeline_input.value).resolve().exists():
            pipeline = OTEPipelineData(filepath=pipeline_input)
        else:
            pipeline = OTEPipelineData(value=pipeline_input)
    else:
        raise TypeError(f"pipeline_input is an unsupported type: {type(pipeline_input)}")

    try:
        pipeline.validate(strict=True)
    except ValidationError as exc:
        raise InputValidationError(exc) from exc

    strategy_configs = {}
    for strategy in pipeline.pydantic_model.strategies:
        config_cls: "Type[GenericConfigData]" = DataFactory(f"execflow.{strategy.get_type()}config")
        config = config_cls(**strategy.get_config())
        config.base.extras.set("strategy_name", strategy.get_name())

        strategy_configs[strategy.get_name()] = config

    return {"result": pipeline, "strategy_configs": strategy_configs}
