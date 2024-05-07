"""Utility AiiDA calculation to update the session for 'function' and 'transformation'
strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiida.engine import calcfunction
from aiida.plugins import DataFactory

if TYPE_CHECKING:  # pragma: no cover
    from aiida.orm import Dict


@calcfunction
def update_oteapi_session(session: Dict, updates: Dict) -> Dict:
    """Return an updated session object."""
    updated_session = session.get_dict()
    updated_session.update(updates.get_dict())
    return DataFactory("core.dict")(updated_session)
