from typing import Optional

from aiida.orm import Dict, SinglefileData, load_node
import dlite
from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, FunctionConfig, SessionUpdate
from oteapi_dlite.models import DLiteSessionUpdate
from oteapi_dlite.utils import get_collection, update_collection
from pydantic import Field
from pydantic.dataclasses import dataclass
from .cuds import DataNode2CUDS
# TODO also report uuid of cuds not just labels


class File2DataNodeConfig(AttrDict):
    """Configuration for a function that casts a file into an AiiDA datanode.
    The AiiDA datanode is then stored in the session.

    """

    path: str = Field(
        description=("Location of file to cast as AiiDA.singlefile DataNode"),
    )

    label: Optional[str] = Field(
        "aiidafilenode",
        description="Label of the datanode????.",
    )
    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description="Configuration options for the local data cache.",
    )


class File2DataNodeFunctionConfig(FunctionConfig):
    """DLite function strategy config."""

    configuration: File2DataNodeConfig = Field(
        ..., description="DLite function strategy-specific configuration."
    )


@dataclass
class File2DataNodeStrategy:
    "Strategy for casting a file into an Aiida SinglefileDataNode"
    function_config: File2DataNodeFunctionConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Initialize strategy."""
        return DLiteSessionUpdate(collection_id=get_collection(session).uuid)

    def get(self, session=None):

        cache = DataCache()

        coll = get_collection(session)
        
        config = self.function_config.configuration

        node = SinglefileData(config.path)
        node.store()
        print('*', node)
        print('**', config.label)
        inst = DataNode2CUDS(node)
        coll.add(config.label, inst)

        print(coll)
        update_collection(coll)
        results = session.get("to_results", dict())
        results[config.label] = node.id
        print('PPPP', results)



        return SessionUpdate(**{"to_results": results})#**{config.label: node.id})
