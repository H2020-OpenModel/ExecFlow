import inspect

from aiida.common.exceptions import MissingEntryPointError
from aiida.orm import Dict, load_code, load_node
from aiida.plugins import DataFactory
from aiida.plugins.entry_point import get_entry_point_from_class
import dlite
import numpy as np
from oteapi.datacache import DataCache
from oteapi.models import AttrDict, FunctionConfig, SessionUpdate
from oteapi_dlite.models import DLiteSessionUpdate
from oteapi_dlite.utils import get_collection, get_driver, update_collection
from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional, Any

# TODO also report uuid of cuds not just labels
@dataclass
class DataNode2CUDSStrategy:
    config: FunctionConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Initialize strategy."""
        return DLiteSessionUpdate(collection_id=get_collection(session).uuid)

    def get(self, session=None):
        update = DLiteSessionUpdate()
        # TODO handle error when node does not exist
        #
        coll = get_collection(session)
        names_list = load_node(session[self.config.configuration["names"]])
        for n in names_list:
            i = DataNode2CUDS(load_node(session[n]))
            coll.add(n, i)
        update_collection(coll)

        return DLiteSessionUpdate(collection_id=coll.uuid)


@dataclass
class CUDS2DataNodeStrategy:
    config: FunctionConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Initialize strategy."""
        return DLiteSessionUpdate(collection_id=get_collection(session).uuid)

    def get(self, session=None):

        cache = DataCache()

        # Choose to use collection defined by node first
        if "collection_uuid" in session:
            coll_id_node = load_node(
                session["collection_uuid"]
            )  # This should be e.g. collection_node_PK
            id_ = coll_id_node.value
            coll = dlite.Collection.from_json(cache.get(id_), id=id_)
        # If there is a collection in the session, use it
        # Problm: we add a collection but then cannot access it?
        # elif 'collection_id' in session:
        #    coll = dlite.get_instance(session.get("collection_id"))
        #    #coll = dlite.get_instance(session['collection_id'])
        #    #coll = dlite.get_collection(id=session['collection_id'])
        else:
            coll = get_collection(session)
        names = load_node(session[self.config.configuration["names"]])
        results = session.get("to_results", dict())
        for n in names:
            i = coll[n]
            d = CUDS2DataNode(i)
            d.store()
            results[n] = d.id

        update_collection(coll)
        return SessionUpdate(**{"to_results": results})


# This function tries to automatically converts an AiiDA DataNode into a dlite Instance.
# Since AiiDA datanodes contain data in an arbitrarily nested fashing (i.e. dict of dicts etc),
# we have to unpack this into only arrays. To retain the nesting information, we annotate the
# Property names with _dict_ to signify a nesting level. E.g. {"kinds": [{"name": "xyz", ...}, {"name": "srt", ...}]}
# will be converted into {"kinds_dict_name": ["xyz", "srt"], ...}.
def DataNode2CUDS(data):
    datname = type(data).__name__
    ep = get_entry_point_from_class(
        class_module=type(data).__module__, class_name=datname
    )[1]
    name = ep.name
    metauri = f"onto-ns.com/meta/1.0/{name}"
    dimnames = {}
    dims = {}
    props = []
    attributes_dict = {}
    # The assumption is that the attributes dict holds all the important data.
    for name in data.attributes:
        gen_property(
            props, dims, dimnames, 0, [], name, data.attributes[name], attributes_dict
        )

    dimns = []
    for x in dimnames:
        for d in dimnames[x]:
            if not any(x == d for x in dimns):
                dimns.append(d)

    Meta = dlite.Instance.create_metadata(
        metauri, dimns, props, f"Inferred metadata for {data.uuid} of type {datname}"
    )

    inst = Meta(dims=[dims["_".join(x.name.split("_")[:-1])][-1] for x in dimns])
    for name in attributes_dict:
        inst[name] = attributes_dict[name]

    return inst


# Here we recursively unpack all the nested data into separate arrays and track the dimensions etc.
# Every time an array of dicts is found the recursion goes one level deeper, and an extra _dict_ is appended
# to the end of the property name.
def gen_property(
    props, dims, dimnames, dim, curid, attributename, attribute, attributes_dict
):
    # TODO: why does dlite not accept pipes ??
    attributename = attributename.replace("|", "__")

    if isinstance(attribute, list):
        dim += 1
        # We are in a potential multidimensional Array.
        # dim keeps track of the current dimension.
        # The assumption is made that all nested data in a list is uniform.
        if dim == 1:
            # First dimension, create a new list of dlite Dimensions,
            # and a list of dimension sizes.
            dims[attributename] = [len(attribute)]
            # Dimensions are named as <attribute>_<dimension>
            dimnames[attributename] = [
                dlite.Dimension(
                    f"{attributename}_{dim}",
                    f"Dimension {dim} of attribute {attributename}",
                )
            ]
        elif dim > len(dims[attributename]):
            # Next dimension -> just append a new dimension
            dims[attributename].append(len(attribute))
            dimnames[attributename].append(
                dlite.Dimension(
                    f"{attributename}_{dim}",
                    f"Dimension {dim} of attribute {attributename}",
                )
            )

        for (i, at) in enumerate(attribute):
            # The integers in id hold the Cartesian Indices into the lists.
            # E.g. d in [[a, b, c], [d, e, f], [h, i, j]] will have ids [2, 1].
            id = curid.copy()
            id.append(i)
            gen_property(
                props, dims, dimnames, dim, id, attributename, at, attributes_dict
            )

    elif isinstance(attribute, dict):
        # Nested data case, set the new attribute name to designate the next level
        # of nesting.
        for name in attribute:
            propname = f"{attributename}_dict_{name}"
            if dim > 0:
                dims[propname] = dims[attributename].copy()
                dimnames[propname] = dimnames[attributename].copy()
            gen_property(
                props,
                dims,
                dimnames,
                dim,
                curid,
                propname,
                attribute[name],
                attributes_dict,
            )

    elif attribute is not None:
        # This is the case for the lowest level of recursion.
        attype = type(attribute)
        attype_name = attype.__name__
        # TODO: This should be handled better by dlite
        if attype_name == "float":
            attype_name = "double"

        if not any(x.name == attributename for x in props):
            # The first element with attributename -> create a new property
            if dim > 0:
                props.append(
                    dlite.Property(
                        attributename,
                        attype_name,
                        [x.name for x in dimnames[attributename]],
                        None,
                        None,
                    )
                )
            else:
                props.append(
                    dlite.Property(attributename, attype_name, None, None, None)
                )

        if dim > 0:
            # We are part of a list of nested data structures
            if attributename not in attributes_dict:
                # First time we come accross a given attribute name, with higher dimension.
                # Since by now we are in the lowest nesting level, we know the dimensions of
                # the multidim array we are part of (kept in dims).
                dims_ = dims[attributename]
                if attype == str:
                    arr = np.empty(dims_, object)
                else:
                    arr = np.empty(dims_, attype)

                arr[tuple([0 for x in dims_])] = attribute
                attributes_dict[attributename] = arr
            else:
                # Set the current entry to the attribute
                attributes_dict[attributename][tuple(curid)] = attribute
        else:
            # Simple case, not part of a list of nested structs
            attributes_dict[attributename] = attribute


# The map from Cuds to an AiiDA DataNode is relatively straightforward, adhering to the rules outlined above.
# Again we instantiate recursively the nested data and fill it with the entries in
# the dlite Instance.
def CUDS2DataNode(cuds):
    # There are some AiiDA DataNodes that behave differently from the usual.
    # We try to capture the main ones here.
    #
    # TODO: There should probably be a global map from name to converting function to which
    # users can add things for other specific cases.
    if cuds.meta.name == "core.code":
        return load_code(cuds.properties["label"])
    if cuds.meta.name == "pseudo.upf":
        from aiida.orm import UpfData

        return UpfData.get_or_create(cuds.properties["filename"])[0]

    # Instantiate the nested datastructure as a basic dict for later use
    att = {}
    for name in cuds.properties:
        construct_attributes(att, name, cuds.properties[name])


    # Here we handle the pipe debacle.
    to_node = {}
    for name in att:
        to_node[name.replace("__", "|")] = att[name]
    # This complication is necessary because sometimes AiiDA DataNodes can not be
    # instantiated as empty, so we try to figure out what the arguments are, look
    # them up in the dlite Instance and fill them out.
    try:
        d = DataFactory(cuds.meta.name)
    except MissingEntryPointError:
        d = DataFactory("core.dict")
    argspec = inspect.getfullargspec(d)
    nargs = len(argspec.args)
    ndef = 0 if argspec.defaults is None else len(argspec.defaults)
    last_arg = nargs - ndef - 1

    args = [to_node[n] if n in to_node else None for n in argspec.args[:last_arg]]

    if len(args) != 0:
        t = d(*args)
    else:
        t = d()

    if isinstance(t, Dict) and cuds.meta.name != 'core.dict':
        t["meta"] = cuds.meta.uri

    # Now we fill in the dlite Instance data into the datanode.
    for name in att:
        t.set_attribute(
            name.replace("__", "|"), att[name]
        )  # The replace here is done because dlite doesn't like pipe
    return t


def construct_attributes(attributes, propertyname, property):
    sname = propertyname.split("_dict_")
    if len(sname) == 1:
        if isinstance(property, np.ndarray):
            attributes[propertyname] = property.tolist()
        else:
            attributes[propertyname] = property
    else:
        if isinstance(property, list) or isinstance(property, np.ndarray):
            if sname[0] not in attributes:
                attributes[sname[0]] = [{} for p in property]

            for (i, p) in enumerate(property):
                construct_attributes(attributes[sname[0]][i], "_".join(sname[1:]), p)
        else:
            if sname[0] not in attributes:
                attributes[sname[0]] = {}

            construct_attributes(attributes[sname[0]], "_".join(sname[1:]), property)

    return attributes
