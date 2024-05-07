from __future__ import annotations

import ast
from pathlib import Path
from urllib.parse import urlsplit

from aiida import orm
from aiida.common.exceptions import AiidaException
from aiida.engine import ExitCode, ToContext, WorkChain, run_get_node, while_
from aiida.engine.utils import is_process_function
from aiida.orm import (
    Data,
    Dict,
    List,
    Node,
    SinglefileData,
    Str,
    load_code,
    load_group,
    load_node,
)
from aiida.plugins import CalculationFactory, DataFactory, WorkflowFactory
from aiida_pseudo.data.pseudo.upf import UpfData
import cachecontrol
from jinja2.nativetypes import NativeEnvironment
import jsonref
from jsonschema import validate
import plumpy
import requests
import yaml

# Copied from https://github.com/aiidalab/aiidalab/blob/90b334e6a473393ba22b915fdaf85d917fd947f4/aiidalab/registry/yaml.py
# licensed under the MIT license
REQUESTS = cachecontrol.CacheControl(requests.Session())


def my_fancy_loader(uri):
    uri_split = urlsplit(uri)
    if Path(uri_split.path).suffix in (".yml", ".yaml"):
        if uri_split.scheme == "file":
            content = Path(uri_split.path).read_bytes()
        else:
            response = REQUESTS.get(uri)
            response.raise_for_status()
            content = response.content
        return yaml.safe_load(content)

    return jsonref.load_uri(uri)


# from jinja2.nativetypes import NativeEnvironment

# TODO: extend schema to include also the postprocess and preprocess objects
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "title": "Chain",
    "properties": {
        "steps": {
            "type": "array",
            "items": {"$ref": "#/definitions/Step"},
            "minItems": 1,
        }
    },
    "required": ["steps"],
    "definitions": {
        "Step": {
            "type": "object",
            "properties": {
                "if": {"type": "string"},
                "while": {"type": "string"},
                "calcjob": {"type": "string"},
                "calculation": {"type": "string"},
                "calcfunction": {"type": "string"},
                "workflow": {"type": "string"},
                "inputs": {"type": "object"},
                "postprocess": {"type": "array"},
                "metadata": {"type": "object"},
                "steps": {"type": "array"},
                "node": {"type": "integer"},
                "error": {"type": "object"},
            },
            "additionalProperties": False,
            "title": "Step",
        }
    },
}

ExitCode_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "title": "ExitCode",
    "required": ["code"],
    "properties": {"code": {"type": "integer"}, "message": {"type": "string"}},
    "additionalProperties": False,
}


structschema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "title": "Structure",
    "required": ["cell", "atoms"],
    "properties": {
        "atoms": {
            "type": "array",
            "items": {"$ref": "#/definitions/Atom"},
            "minItems": 1,
        },
        "cell": {"$ref": "#/definitions/Cell"},
    },
    "definitions": {
        "Atom": {
            "type": "object",
            "properties": {
                "symbols": {"type": "string"},
                "position": {"$ref": "#/definitions/Vec3"},
            },
            "required": ["symbols", "position"],
        },
        "Cell": {
            "type": "array",
            "items": {"$ref": "#/definitions/Vec3"},
            "required": ["a", "b", "c"],
            "properties": {
                "a": {"$ref": "#/definitions/Vec3"},
                "b": {"$ref": "#/definitions/Vec3"},
                "c": {"$ref": "#/definitions/Vec3"},
            },
        },
        "Vec3": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
        },
    },
}

upfschema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "title": "UpfData",
    "required": ["group", "element"],
    "properties": {"group": {"type": "string"}, "element": {"type": "string"}},
}


def dict2structure(d):
    validate(instance=d, schema=structschema)
    structure = DataFactory("core.structure")(cell=d["cell"])
    for a in d["atoms"]:
        structure.append_atom(**a)
    return structure


def dict2code(d):
    return load_code(d)


def dict2upf(d):
    validate(instance=d, schema=upfschema)
    group = load_group(d["group"])
    return group.get_pseudo(element=d["element"])


# TODO: implement for old upfs?
def dict2upf_deprecated(_):
    return None


def dict2kpoints(d):
    kpoints = DataFactory("core.array.kpoints")()
    if isinstance(d[0], list):
        kpoints.set_kpoints(d)
    else:
        kpoints.set_kpoints_mesh(d)
    return kpoints


def dict2datanode(dat, typ, dynamic=False):
    # Resolve recursively
    if dynamic:
        out = {}
        for k in dat:
            # Is there only 1 level of dynamisism?
            out[k] = dict2datanode(dat[k], typ, False)
        return out

    # If node is specified, just load node
    if dat is dict and "node" in dat:
        return load_node(dat["node"])

    # Else resolve DataNode from value
    if typ is orm.AbstractCode:
        return dict2code(dat)
    if typ is orm.StructureData:
        return dict2structure(dat)
    if typ is UpfData or typ is orm.nodes.data.upf.UpfData:
        return dict2upf(dat)
    if typ is orm.KpointsData:
        return dict2kpoints(dat)
    if typ is Dict:
        return Dict(dict=dat)
    if typ is List:
        return List(list=dat)
    if typ is Data:
        return dat
    return typ(dat)


def get_dot2index(d, key):
    if isinstance(key, str):
        return get_dot2index(d, key.split("."))

    if len(key) == 1:
        return d[key[0]]

    return get_dot2index(d[key[0]], key[1:])


def set_dot2index(d, key, val):
    if isinstance(key, str):
        return set_dot2index(d, key.split("."), val)

    if len(key) == 1:
        d[key[0]] = val
        return None

    t = key[0]
    if t not in d:
        d[t] = {}

    return set_dot2index(d[t], key[1:], val)


class DeclarativeChain(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input("workchain_specification", valid_type=(SinglefileData, Str))
        spec.exit_code(2, "ERROR_SUBPROCESS", message="A subprocess has failed.")

        spec.outline(
            cls.setup,
            while_(cls.not_finished)(cls.submit_next, cls.process_current),
            cls.finalize,
        )
        spec.output_namespace("results", dynamic=True)

    def setup(self):
        self.ctx.current_id = 0
        self.ctx.results = {}
        if isinstance(self.inputs["workchain_specification"], Str):
            full_file = Path(self.inputs["workchain_specification"].value).resolve()
            d = full_file.parent
            ext = full_file.suffix

            with full_file.open() as f:
                s = f.read()
                s = s.replace("__DIR__", d)
                if ext in (".yaml", ".yml"):
                    tspec = yaml.safe_load(s)
                    spec = jsonref.JsonRef.replace_refs(tspec, loader=my_fancy_loader)
                else:
                    spec = jsonref.load(s)

        else:
            ext = Path(self.inputs["workchain_specification"].filename).suffix
            with self.inputs["workchain_specification"].open(mode="r") as f:
                if ext in (".yaml", ".yml"):
                    tspec = yaml.safe_load(f.read())
                    spec = jsonref.JsonRef.replace_refs(tspec, loader=my_fancy_loader)
                else:
                    spec = jsonref.load(f)

        validate(instance=spec, schema=schema)
        self.ctx.steps = spec["steps"]
        self.env = NativeEnvironment()
        self.env.filters["to_ctx"] = self.to_ctx
        self.env.filters["to_results"] = self.to_results

        self.ctx.in_while = False

        if "setup" in spec:
            for k in spec["setup"]:
                self.eval_template(k)

    def not_finished(self):
        return self.ctx.current_id < len(self.ctx.steps)

    def submit_next(self):
        n = self.next_step()

        if isinstance(n, Node):
            self.ctx.current = n
            return None

        cjob, inputs = n
        if is_process_function(cjob):
            return ToContext(current=run_get_node(cjob, **inputs)[1])
        return ToContext(current=self.submit(cjob, **inputs))

    def next_step(self):

        id = self.ctx.current_id
        step = self.ctx.steps[id]

        if "if" in step and not self.eval_template(step["if"]):
            self.ctx.current_id += 1
            return self.next_step()

        if "while" in step:
            if self.eval_template(step["while"]):
                if not self.ctx.in_while:
                    # Enter the while loop
                    self.ctx.in_while = True
                    self.ctx.while_first_id = len(self.ctx.steps)
                    self.ctx.while_entry_id = id
                    self.ctx.steps += step["steps"]
                    self.ctx.current_id = self.ctx.while_first_id
                else:
                    # Reroll the while loop
                    self.ctx.current_id = self.ctx.while_first_id

            elif self.ctx.in_while:
                # Cleanup while loop
                self.ctx.in_while = False
                self.ctx.steps = self.ctx.steps[0 : -len(step["steps"])]
                self.ctx.current_id += 1

            return self.next_step()

        if "node" in step:
            return load_node(step["node"])

        if any(_ in step for _ in ("calcjob", "workflow", "calculation", "calcfunction")):
            # This needs to happen because no dict 2 node for now.
            # M inputs = dict()
            if "calcjob" in step:
                cjob = CalculationFactory(step["calcjob"])
            elif "calcfunction" in step:
                cjob = CalculationFactory(step["calcfunction"])
            elif "calculation" in step:
                cjob = CalculationFactory(step["calculation"])
            elif "workflow" in step:
                cjob = WorkflowFactory(step["workflow"])
            else:
                ValueError(f"Unrecognized step {step}")

            spec_inputs = cjob.spec().inputs
            inputs = self.resolve_inputs(step["inputs"], spec_inputs)
            return cjob, inputs

        raise ValueError(f"Unrecognized step {step}")

    def resolve_inputs(self, inputs, spec_inputs):
        out = {}
        for k in inputs:

            # First resolve enforced types with 'type' and 'value', and dereference ctx vars
            val = self.resolve_input(inputs[k])
            # Now we resolve potential required types of the calcjob
            valid_type = None
            if k in spec_inputs:
                i = spec_inputs.get(k)
                valid_type = i.valid_type

                if valid_type is None:
                    set_dot2index(
                        out, k, orm.to_aiida_type(val) if not (isinstance(val, orm.Data) or k == "metadata") else val
                    )
                    continue

                if isinstance(val, valid_type):
                    set_dot2index(out, k, val)
                    continue

                if isinstance(valid_type, tuple):
                    inval = None
                    c = 0
                    while inval is None and c < len(valid_type):
                        try:
                            inval = dict2datanode(val, valid_type[c], isinstance(i, plumpy.PortNamespace))
                        except AiidaException:
                            inval = None
                        c += 1

                    if inval is None:
                        ValueError(f"Couldn't resolve type of input {k}")
                else:
                    inval = dict2datanode(val, valid_type, isinstance(i, plumpy.PortNamespace))
                    if inval is None:
                        ValueError(f"Couldn't resolve input {k}")

                set_dot2index(out, k, inval)

            else:
                set_dot2index(out, k, orm.to_aiida_type(val) if not isinstance(val, orm.Data) else val)

        return out

    def resolve_input(self, input):
        if isinstance(input, dict):
            # If 'value' and 'type' are in dict we assume lowest level, otherwise recurse
            if "value" in input and "type" in input:
                try:
                    valid_type = DataFactory(input["type"])
                except AiidaException:
                    valid_type = ast.literal_eval(input["type"])  # Other classes

                return dict2datanode(self.resolve_input(input["value"]), valid_type)
            # Normal dict, recurse
            for k in input:
                input[k] = self.resolve_input(input[k])
            return input

        if isinstance(input, list):
            list_s = []
            for element in input:
                list_s.append(self.resolve_input(element))

            return list_s
        # not a dict, just a value so let's just dereference and retur
        return self.eval_template(input)

    def process_current(self):
        step = self.ctx.steps[self.ctx.current_id]

        if not self.ctx.current.is_finished_ok:
            self.report(
                f"A subprocess failed with exit status {self.ctx.current.exit_status}: {self.ctx.current.exit_message}"
            )
            if "error" in step:
                validate(step["error"], schema=ExitCode_schema)
                return (
                    ExitCode(step["error"]["code"])
                    if "message" not in step["error"]
                    else ExitCode(step["error"]["code"], message=step["error"]["message"])
                )

        if "postprocess" in step:
            for k in step["postprocess"]:
                self.eval_template(k)

        self.ctx.current_id += 1

        if self.ctx.in_while and self.ctx.current_id == len(self.ctx.steps):
            self.ctx.current_id = self.ctx.while_entry_id

        return None

    # Jinja evaluation
    def eval_template(self, s):
        if isinstance(s, str) and "{{" in s and "}}" in s:
            return self.env.from_string(s).render(ctx=self.ctx)
        return s

    # Jinja Filters
    def to_ctx(self, value, key):
        self.ctx[key] = value
        return value

    def to_results(self, value, key):
        self.ctx.results[key] = value
        return value

    def finalize(self):
        self.out("results", self.ctx.results)
