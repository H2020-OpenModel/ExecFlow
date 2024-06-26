from __future__ import annotations

from typing import Annotated, Any

from aiida.orm import Dict
import dlite
from oteapi.models import AttrDict, DataCacheConfig, FunctionConfig, SessionUpdate
from oteapi_dlite.models import DLiteSessionUpdate
from oteapi_dlite.utils import get_collection, update_collection
from pydantic import Field
from pydantic.dataclasses import dataclass

# TODO also report uuid of cuds not just labels


class File2CollectionConfig(AttrDict):
    """Configuration for a function that casts a file into an AiiDA datanode.
    The AiiDA datanode is then stored in the session.

    """

    path: Annotated[
        str,
        Field(
            description=("Location of file to cast as AiiDA.singlefile DataNode"),
        ),
    ]
    label: Annotated[
        str | None,
        Field(
            description="Label of the file.",
        ),
    ] = "filename"
    datacache_config: Annotated[
        DataCacheConfig | None,
        Field(
            description="Configuration options for the local data cache.",
        ),
    ] = None


class File2CollectionFunctionConfig(FunctionConfig):
    """DLite function strategy config."""

    configuration: Annotated[
        File2CollectionConfig, Field(description="DLite function strategy-specific configuration.")
    ]


@dataclass
class File2CollectionStrategy:
    "Strategy for casting a file into an Aiida SinglefileDataNode"
    function_config: File2CollectionFunctionConfig

    def initialize(self, session: Dict[str, Any] | None = None) -> SessionUpdate:
        """Initialize strategy."""
        return DLiteSessionUpdate(collection_id=get_collection(session).uuid)

    def get(self, session=None):

        coll = get_collection(session)

        config = self.function_config.configuration

        meta = dlite.get_instance("onto-ns.com/meta/1.0/core.singlefile")
        inst = meta()
        inst.filename = config.path
        coll.add(config.label, inst)

        update_collection(coll)

        return SessionUpdate()  # **{"to_results": results})#**{config.label: node.pk})
