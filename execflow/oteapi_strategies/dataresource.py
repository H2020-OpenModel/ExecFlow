"""AiiDA Process for the OTE Data Resource Strategy.

Since OTE Data Resource strategies may not subsequently invoke other AiiDA Workflows or
Calculations, it is semantically equivalent to an AiiDA Calculation.
"""
from typing import TYPE_CHECKING

from aiida.engine import calcfunction
from aiida.plugins import DataFactory
from oteapi.plugins import create_strategy, load_strategies

if TYPE_CHECKING:  # pragma: no cover
    from aiida.orm import Dict

    from execflow.wrapper.data.resourceconfig import ResourceConfigData


@calcfunction
def init_dataresource(config: "ResourceConfigData", session: "Dict") -> "Dict":
    """Initialize an OTE Data Resource strategy."""
    load_strategies()

    if config.downloadUrl and config.mediaType:
        # Download strategy
        session_update = create_strategy("download", config.get_dict()).initialize(
            session.get_dict()
        )

        # Parse strategy
        parse_session = session.get_dict()
        parse_session.update(session_update)
        session_update = create_strategy("parse", config.get_dict()).initialize(
            session.get_dict()
        )
    elif config.accessUrl and config.accessService:
        # Resource strategy
        session_update = create_strategy("resource", config.get_dict()).initialize(
            session.get_dict()
        )
    else:
        raise ValueError(
            "Either of the pairs downloadUrl/mediaType and accessUrl/accessService "
            "must be defined in the config."
        )

    updated_session = session.get_dict()
    updated_session.update(session_update)
    return DataFactory("core.dict")(updated_session)


@calcfunction
def get_dataresource(config: "ResourceConfigData", session: "Dict") -> "Dict":
    """Get/Execute an OTE Data Resource strategy."""
    load_strategies()

    if config.downloadUrl and config.mediaType:
        # Download strategy
        session_update = create_strategy("download", config.get_dict()).get(
            session.get_dict()
        )

        # Parse strategy
        parse_session = session.get_dict()
        parse_session.update(session_update)
        session_update = create_strategy("parse", config.get_dict()).get(parse_session)
    elif config.accessUrl and config.accessService:
        # Resource strategy
        session_update = create_strategy("resource", config.get_dict()).get(
            session.get_dict()
        )
    else:
        raise ValueError(
            "Either of the pairs downloadUrl/mediaType and accessUrl/accessService "
            "must be defined in the config."
        )

    updated_session = session.get_dict()
    updated_session.update(session_update)
    return DataFactory("core.dict")(updated_session)
