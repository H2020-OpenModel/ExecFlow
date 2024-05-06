from __future__ import annotations

from io import StringIO

from aiida.engine import ToContext, WorkChain, calcfunction
from aiida.orm import Dict, SinglefileData, Str
from aiida_shell import ShellJob
from aiida_shell.launch import prepare_code
import chevron


@calcfunction
def fill_template(template: SinglefileData, parameters: Dict):
    content = template.get_content()
    out = chevron.render(content, parameters.get_dict())
    return SinglefileData(StringIO(out))


class ExecWrapper(WorkChain):

    @classmethod
    def define(cls, spec):
        super().define(spec)

        spec.input("files", valid_type=(Dict, dict), is_metadata=True)
        spec.input("command", valid_type=Str)
        spec.expose_inputs(ShellJob, exclude=["nodes", "filenames", "code", "metadata"])
        spec.expose_inputs(ShellJob, include=["metadata"], namespace="shelljob")

        spec.outline(cls.setup, cls.register_code, cls.submit_shell, cls.finalize)

        spec.outputs.dynamic = True

    def setup(self):

        self.ctx.filenodes = {}
        self.ctx.filenames = {}
        for k, f in self.inputs.files.items():
            if "node" in f:
                self.ctx.filenodes[k] = f["node"]
            else:
                self.ctx.filenodes[k] = fill_template(SinglefileData(f["template"]), f.get("parameters", Dict()))
            self.ctx.filenames[k] = f["filename"]

    def register_code(self):
        computer = (self.inputs.shelljob.metadata or {}).get("options", {}).get("computer", None)
        self.ctx.code = prepare_code(str(self.inputs.command.value), computer)

    def submit_shell(self):
        inputs = {
            "code": self.ctx.code,
            "nodes": self.ctx.filenodes,
            "filenames": self.ctx.filenames,
            **self.exposed_inputs(ShellJob),
        }

        # if 'metadata' in self.inputs.shelljob:
        #    inputs['metadata'] =  self.inputs.shelljob.metadata
        # else:
        # This if else from Louis did not work.
        inputs["metadata"] = {"options": {"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1}}}

        shell = self.submit(ShellJob, **inputs)
        return ToContext(shell=shell)  # nosec

    def finalize(self):
        for k in self.ctx.shell.outputs:
            self.out(f"{k}", self.ctx.shell.outputs[k])
