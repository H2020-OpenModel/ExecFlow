"""Pytest-specific file for fixtures and configuration.

Since this `conftest` file is at the root level of the `tests` folder, all fixtures
here are available for all tests.

Use AiiDA's pytest fixtures.
Look inside aiida.manage.tests.pytest_fixtures to see which fixtures are provided:
https://aiida.readthedocs.io/projects/aiida-core/en/latest/reference/apidoc/aiida.manage.tests.html#module-aiida.manage.tests.pytest_fixtures
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest_plugins = ["aiida.manage.tests.pytest_fixtures"]


@pytest.fixture(autouse=True)
def _aiida_profile_clean_auto(aiida_profile_clean):  # noqa: ARG001
    """Automatically clear the AiiDA profile's DB and storage after each test."""


@pytest.fixture(scope="session")
def samples() -> Path:
    """Return path to 'samples' folder."""

    path = (Path(__file__).resolve().parent / "samples").resolve()
    if not path.exists():
        raise FileNotFoundError(f"Could not locate the 'samples' folder at: {path}")
    return path


@pytest.fixture()
def fixture_localhost(aiida_localhost):
    """Return a localhost `Computer`."""
    localhost = aiida_localhost
    localhost.set_default_mpiprocs_per_machine(1)
    return localhost


@pytest.fixture()
def generate_calcjob_node(fixture_localhost):
    """Fixture to generate a mock `CalcJobNode` for testing parsers."""

    def _generate_calc_job_node(entry_point):
        """Fixture to generate a mock `CalcJobNode` for testing parsers.

        :param entry_point: entry point name of the calculation class
        """
        from aiida import orm

        return orm.CalcJobNode(computer=fixture_localhost, process_type=entry_point)

    return _generate_calc_job_node


@pytest.fixture()
def generate_workchain():
    """Generate an instance of a `WorkChain`."""

    def _generate_workchain(entry_point, inputs):
        """Generate an instance of a `WorkChain` with the given entry point and inputs.

        :param entry_point: entry point name of the work chain subclass.
        :param inputs: inputs to be passed to process construction.
        :return: a `WorkChain` instance.
        """
        from aiida.engine.utils import instantiate_process
        from aiida.manage.manager import get_manager
        from aiida.plugins import WorkflowFactory

        process_class = WorkflowFactory(entry_point)
        runner = get_manager().get_runner()
        return instantiate_process(runner, process_class, **inputs)

    return _generate_workchain


@pytest.fixture()
def generate_declarative_workchain(generate_workchain):
    """Generate an instance of a ``PwBaseWorkChain``."""

    def _generate_declarative_workchain(input):
        """Generate an instance of a ``PwBaseWorkChain``.

        :param exit_code: exit code for the ``PwCalculation``.
        :param inputs: inputs for the ``PwBaseWorkChain``.
        :param return_inputs: return the inputs of the ``PwBaseWorkChain``.
        :param pw_outputs: ``dict`` of outputs for the ``PwCalculation``. The keys must correspond to the link labels
            and the values to the output nodes.
        """
        from io import StringIO

        from aiida.orm import SinglefileData

        entry_point = "execflow.declarative"
        if isinstance(input, Path):
            input = SinglefileData(input)
        elif isinstance(input, str):
            input = SinglefileData(StringIO(input))

        elif not isinstance(input, SinglefileData):
            raise ValueError("input needs to be SinglefileData or a str")

        return generate_workchain(entry_point, {"workchain_specification": input})

    return _generate_declarative_workchain
