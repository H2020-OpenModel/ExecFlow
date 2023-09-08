"""Test execflow.wrapper.data.declarative_pipeline"""
# pylint: disable=too-many-locals,invalid-name
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Dict, Tuple, Type, Union

    from execflow.wrapper.data.declarative_pipeline import (
        OTEPipelineData as OTEPipelineDataNode,
    )


@pytest.mark.parametrize(
    "value_type",
    (
        dict,
        "execflow.oteapi_pipeline",
        "core.dict",
        "DeclarativePipeline",
        str,
        bytes,
        "core.str",
    ),
)
def test_initialization_strategies_value(
    value_type: "Union[Type[Union[dict, str, bytes]], str]", samples: "Path"
) -> None:
    """Ensure the different intended initialization strategies work.

    This test is for the `value` pathway, i.e., using the `value` parameter.

    Parameters:
        value_type: One of the valid types for the `value` parameter.
        samples: Path to test directory with sample files.

    """
    from copy import deepcopy

    from aiida.plugins import DataFactory
    import yaml

    from execflow.data.oteapi.declarative_pipeline import DeclarativePipeline

    OTEPipelineData: "Type[OTEPipelineDataNode]" = DataFactory(
        "execflow.oteapi_pipeline"
    )
    declarative_pipeline_file: "Dict[str, Any]" = yaml.safe_load(
        (samples / "pipe.yml").read_bytes()
    )

    if isinstance(value_type, type):
        if value_type == dict:
            pipeline_input = deepcopy(declarative_pipeline_file)
            assert isinstance(pipeline_input, dict)
            node = OTEPipelineData(value=pipeline_input)
        elif value_type == str:
            node = OTEPipelineData(
                value=(samples / "pipe.yml").read_text(encoding="utf8")
            )
        else:
            assert value_type == bytes, f"Unknown value_type type: {value_type}"
            node = OTEPipelineData(value=(samples / "pipe.yml").read_bytes())
    else:
        # value_type is a string
        if value_type == "DeclarativePipeline":
            pydantic_input = deepcopy(declarative_pipeline_file)
            pydantic_model = DeclarativePipeline(**pydantic_input)
            node = OTEPipelineData(value=pydantic_model)
        elif value_type == "execflow.oteapi_pipeline":
            pipeline_data_node = OTEPipelineData()
            pipeline_data_node.version = declarative_pipeline_file["version"]
            pipeline_data_node.strategies = declarative_pipeline_file["strategies"]
            pipeline_data_node.pipelines = declarative_pipeline_file["pipelines"]
            node = OTEPipelineData(value=pipeline_data_node)
        elif value_type == "core.dict":
            dict_node_input = deepcopy(declarative_pipeline_file)
            aiida_dict_node = DataFactory(value_type)(dict_node_input)
            node = OTEPipelineData(value=aiida_dict_node)
        else:
            assert value_type == "core.str", f"Unknown value_type given: {value_type}"
            aiida_str_node = DataFactory(value_type)(
                (samples / "pipe.yml").read_text(encoding="utf8")
            )
            node = OTEPipelineData(value=aiida_str_node)

    assert node.validate() is None
    assert node.version == int(declarative_pipeline_file["version"])
    assert node.pipelines == dict(declarative_pipeline_file["pipelines"])

    if value_type == "DeclarativePipeline":
        # A lot of default values will be added to the strategies from the pydantic
        # model(s).
        assert node.strategies != list(declarative_pipeline_file["strategies"])

        # Initialize pydantic model and convert strategies to a list of dictionaries.
        pydantic_input = deepcopy(declarative_pipeline_file)
        pydantic_model = DeclarativePipeline(**pydantic_input)
        assert node.strategies == [_.dict() for _ in pydantic_model.strategies]
    else:
        assert node.strategies == list(declarative_pipeline_file["strategies"])


@pytest.mark.parametrize(
    "input_type",
    (
        "Path",
        str,
        "core.str",
        "core.singlefile",
    ),
)
def test_initialization_strategies_file(
    input_type: "Union[Type[str], str]", samples: "Path"
) -> None:
    """Ensure the different intended initialization strategies work.

    This test is for the file pathway, i.e., using the `filepath` or `single_file`
    parameter.

    Parameters:
        input_type: One of the valid types for the `filepath` or `single_file`
            parameter.
        samples: Path to test directory with sample files.

    """
    from aiida.plugins import DataFactory
    import yaml

    OTEPipelineData: "Type[OTEPipelineDataNode]" = DataFactory(
        "execflow.oteapi_pipeline"
    )
    declarative_pipeline_file: "Dict[str, Any]" = yaml.safe_load(
        (samples / "pipe.yml").read_bytes()
    )

    if input_type == str:
        # filepath
        node = OTEPipelineData(filepath=str(samples / "pipe.yml"))
    else:
        assert isinstance(input_type, str)

        # filepath
        if input_type == "Path":
            node = OTEPipelineData(filepath=samples / "pipe.yml")
        elif input_type == "core.str":
            aiida_str_node = DataFactory(input_type)(str(samples / "pipe.yml"))
            node = OTEPipelineData(filepath=aiida_str_node)

        # single_file
        else:
            assert (
                input_type == "core.singlefile"
            ), f"Unknown input_type given: {input_type}"

            aiida_singlefile_node = DataFactory(input_type)(samples / "pipe.yml")
            node = OTEPipelineData(single_file=aiida_singlefile_node)

    assert node.validate() is None
    assert node.version == int(declarative_pipeline_file["version"])
    assert node.pipelines == dict(declarative_pipeline_file["pipelines"])
    assert node.strategies == list(declarative_pipeline_file["strategies"])


def test_initialization_strategies_explicit(samples: "Path") -> None:
    """Ensure the different intended initialization strategies work.

    This test is for explicitly filling out the top keywords.
    I.e., `version`, `strategies`, and `pipelines`.

    Parameters:
        samples: Path to test directory with sample files.

    """
    from copy import deepcopy

    from aiida.plugins import DataFactory
    import yaml

    OTEPipelineData: "Type[OTEPipelineDataNode]" = DataFactory(
        "execflow.oteapi_pipeline"
    )
    declarative_pipeline_file: "Dict[str, Any]" = yaml.safe_load(
        (samples / "pipe.yml").read_bytes()
    )

    # Create Node from __init__ directly
    copy_file = deepcopy(declarative_pipeline_file)
    node = OTEPipelineData(
        version=copy_file["version"],
        strategies=copy_file["strategies"],
        pipelines=copy_file["pipelines"],
    )

    assert node.validate() is None
    assert node.version == int(declarative_pipeline_file["version"])
    assert node.pipelines == dict(declarative_pipeline_file["pipelines"])
    assert node.strategies == list(declarative_pipeline_file["strategies"])

    # Create Node through setting properties individually after initializing an "empty"
    # Node.
    copy_file = deepcopy(declarative_pipeline_file)
    node = OTEPipelineData()
    node.version = copy_file["version"]
    node.strategies = copy_file["strategies"]
    node.pipelines = copy_file["pipelines"]

    assert node.validate() is None
    assert node.version == int(declarative_pipeline_file["version"])
    assert node.pipelines == dict(declarative_pipeline_file["pipelines"])
    assert node.strategies == list(declarative_pipeline_file["strategies"])


@pytest.mark.parametrize(
    "input_keys",
    [
        ("strategies", "pipelines"),
        ("version", "strategies", "pipelines"),
    ],
    ids=["strat+pipe", "ver+strat+pipe"],
)
def test_validate_valid_cases(input_keys: "Tuple[str, ...]", samples: "Path") -> None:
    """Test various valid cases for validation.

    Parameters:
        input_keys: Input keys for OTEPipelineData from declarative pipeline file.
        samples: Path to test directory with sample files.

    """
    from copy import deepcopy

    from aiida.plugins import DataFactory
    import yaml

    OTEPipelineData: "Type[OTEPipelineDataNode]" = DataFactory(
        "execflow.oteapi_pipeline"
    )
    declarative_pipeline_file: "Dict[str, Any]" = yaml.safe_load(
        (samples / "pipe.yml").read_bytes()
    )

    node = OTEPipelineData(
        **{key: deepcopy(declarative_pipeline_file[key]) for key in input_keys}
    )
    assert node.validate() is None


@pytest.mark.parametrize(
    "input_keys",
    [
        ("strategies",),
        ("pipelines",),
        ("version",),
        ("version", "strategies"),
        ("version", "pipelines"),
    ],
    ids=["strat", "pipe", "ver", "ver+strat", "ver+pipe"],
)
@pytest.mark.skip(reason="Issues with validation, needs fixing")
def test_validate_invalid_cases(input_keys: "Tuple[str, ...]", samples: "Path") -> None:
    """Test various invalid cases for validation.

    Parameters:
        input_keys: Input keys for OTEPipelineData from declarative pipeline file.
        samples: Path to test directory with sample files.

    """
    from copy import deepcopy

    from aiida.common.exceptions import ValidationError
    from aiida.plugins import DataFactory
    import yaml

    OTEPipelineData: "Type[OTEPipelineDataNode]" = DataFactory(
        "execflow.oteapi_pipeline"
    )
    declarative_pipeline_file: "Dict[str, Any]" = yaml.safe_load(
        (samples / "pipe.yml").read_bytes()
    )

    node = OTEPipelineData(
        **{key: deepcopy(declarative_pipeline_file[key]) for key in input_keys}
    )

    exception_message_end = ""
    if "strategies" not in input_keys:
        exception_message_end += " strategies"
    if "strategies" not in input_keys and "pipelines" not in input_keys:
        exception_message_end += " and"
    if "pipelines" not in input_keys:
        exception_message_end += " pipelines"

    assert node.validate(strict=False) is None
    with pytest.raises(
        ValidationError, match=rf"^Cannot validate, missing{exception_message_end}$"
    ):
        node.validate(strict=True)
