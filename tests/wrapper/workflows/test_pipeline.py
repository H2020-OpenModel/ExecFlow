"""Test execflow.wrapper.workflows.pipeline"""
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Dict, Tuple, Union


def get_input_variants() -> "Dict[str, Tuple[str, Union[Path, bytes, dict]]]":
    """Input for 'test_run_pipeline'.

    Must pass AiiDA input variants as tuples of entry point entries and initialization
    object to the AiiDA Data Node type.
    This is because the AiiDA Profile (DB/storage) is not created/initialized until
    actually entering a test. And this function is *not* a test.
    """
    from pathlib import Path

    import yaml

    samples = (Path(__file__).resolve().parent.parent.parent / "samples").resolve()

    return {
        "SinglefileData": ("core.singlefile", samples / "pipe.yml"),
        "Str path": ("core.str", str(samples / "pipe.yml")),
        "Str content": (
            "core.str",
            (samples / "pipe.yml").read_text(encoding="utf8"),
        ),
        "OTEPipelineData": (
            "execflow.oteapi_pipeline",
            (samples / "pipe.yml").read_bytes(),
        ),
        "orm.Dict": (
            "core.dict",
            yaml.safe_load((samples / "pipe.yml").read_bytes()),
        ),
    }


@pytest.mark.parametrize(
    ["entry_point", "node_input"],
    get_input_variants().values(),
    ids=get_input_variants().keys(),
)
def test_run_pipeline(entry_point: str, node_input: "Union[Path, str, dict]") -> None:
    """Run a simple pipeline.

    Parameters:
        entry_point: An AiiDA entry point for Data Nodes.
        node_input: Input for initializing the given Data Node.

    """
    from aiida.engine import run
    from aiida.plugins import DataFactory

    from execflow.workchains.oteapi_pipeline import OTEPipeline

    input_variant = DataFactory(entry_point)(node_input)
    run(OTEPipeline, pipeline=input_variant)


def test_result_pipeline(samples: "Path") -> None:
    """Run a simple pipeline and check result.

    Parameters:
        samples: Path to test directory with sample files.

    """
    from aiida.engine import run
    from aiida.plugins import DataFactory
    import requests
    import yaml

    from execflow.workchains.oteapi_pipeline import OTEPipeline

    entry_point, node_input = get_input_variants()["OTEPipelineData"]
    input_variant = DataFactory(entry_point)(node_input)
    result = run(OTEPipeline, pipeline=input_variant)

    assert len(result) == 1
    assert "session" in result
    assert isinstance(result["session"], DataFactory("core.dict"))

    declarative_pipeline_file = yaml.safe_load((samples / "pipe.yml").read_bytes())
    json_file = requests.get(
        declarative_pipeline_file["strategies"][0]["downloadUrl"],
        timeout=5,
    ).json()

    # The JSON parser strategy will add a "content" entry in the session.
    # This will contain the parsed content.
    assert "content" in result["session"]
    assert result["session"]["content"] == json_file

    # The mapping strategy will add "prefixes" and "triples" entries in the session.
    assert "prefixes" in result["session"]
    assert "triples" in result["session"]
    assert (
        result["session"]["prefixes"]
        == declarative_pipeline_file["strategies"][1]["prefixes"]
    )
    for triple in result["session"]["triples"]:
        assert triple in declarative_pipeline_file["strategies"][1]["triples"]
