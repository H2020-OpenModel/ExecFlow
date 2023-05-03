"""Pytest-specific file for fixtures and configuration.

Since this `conftest` file is at the root level of the `tests` folder, all fixtures
here are available for all tests.

Use AiiDA's pytest fixtures.
Look inside aiida.manage.tests.pytest_fixtures to see which fixtures are provided:
https://aiida.readthedocs.io/projects/aiida-core/en/latest/reference/apidoc/aiida.manage.tests.html#module-aiida.manage.tests.pytest_fixtures
"""
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

pytest_plugins = ["aiida.manage.tests.pytest_fixtures"]


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.usefixtures("aiida_profile_clean")
def aiida_profile_clean_auto():
    """Automatically clear the AiiDA profile's DB and storage after each test."""


@pytest.fixture(scope="session")
def samples() -> "Path":
    """Return path to 'samples' folder."""
    from pathlib import Path

    path = (Path(__file__).resolve().parent / "samples").resolve()
    if not path.exists():
        raise FileNotFoundError(f"Could not locate the 'samples' folder at: {path}")
    return path
