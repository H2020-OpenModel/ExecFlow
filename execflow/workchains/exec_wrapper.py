from __future__ import annotations

from aiida.engine import ExitCode, ToContext, WorkChain, run_get_node, while_, calcfunction
import pathlib
import typing as t
from io import StringIO
from typing import TYPE_CHECKING

from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.folders import Folder
from aiida.engine import CalcJob, CalcJobProcessSpec
from aiida.orm import Data, Dict, List, SinglefileData, to_aiida_type, Str
from aiida_shell.engine.launchers.shell_job import prepare_code
from aiida_shell import ShellJob
import chevron

@calcfunction
def fill_template(template: SingleFileData, parameters: Dict):
    content =  template.get_content()
    out = chevron.render(content, parameters.get_dict())
    return SinglefileData(StringIO(out))

class ExecWrapper(WorkChain):

    @classmethod
    def define(cls, spec):
        super().define(spec)

        spec.input("files", valid_type=Dict)
        spec.input("command", valid_type = Str)
        spec.expose_inputs(ShellJob, exclude=['nodes', 'filenames', 'code', 'metadata'])

        spec.outline(
            cls.setup,
            cls.register_code,
            cls.submit_shell,
            cls.finalize
        )

        spec.expose_outputs(ShellJob)

    def setup(self):

        self.ctx.filenodes = dict()
        self.ctx.filenames = dict()
        for k, f in self.inputs.files.items():
            self.ctx.filenodes[k] = fill_template(SinglefileData(f['template']), f['parameters'])
            self.ctx.filenames[k] = f['filename']

    def register_code(self):
        computer = (self.inputs.metadata or {}).get('options', {}).pop('computer', None)
        self.ctx.code = prepare_code(str(self.inputs.command.value), computer)
        return

    def submit_shell(self):
        inputs = {'code': self.ctx.code,
                  'nodes': self.ctx.filenodes,
                  'filenames': self.ctx.filenames,
                  **self.exposed_inputs(ShellJob)}



        shell = self.submit(ShellJob, **inputs)
        return ToContext(shell=shell)

    def finalize(self):
        self.out_many(self.exposed_outputs(self.ctx.shell, ShellJob))


