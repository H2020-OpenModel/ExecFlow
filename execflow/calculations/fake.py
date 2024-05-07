from __future__ import annotations

from aiida import orm
from aiida.engine import CalcJob
from aiida.plugins import DataFactory

LegacyUpfData = DataFactory("core.upf")
UpfData = DataFactory("pseudo.upf")


class FakeQEPW(CalcJob):
    @classmethod
    def define(cls, spec):
        """Define the process specification."""
        super().define(spec)
        spec.input("metadata.options.withmpi", valid_type=bool, default=True)  # Override default withmpi=False
        spec.input("structure", valid_type=orm.StructureData, help="The input structure.")
        spec.input(
            "parameters",
            valid_type=orm.Dict,
            help="The input parameters that are to be used to construct the input file.",
        )
        spec.input(
            "settings",
            valid_type=orm.Dict,
            required=False,
            help="Optional parameters to affect the way the calculation job and the parsing are performed.",
        )
        spec.input(
            "parent_folder",
            valid_type=orm.RemoteData,
            required=False,
            help="An optional working directory of a previously completed calculation to restart from.",
        )
        spec.input(
            "vdw_table",
            valid_type=orm.SinglefileData,
            required=False,
            help="Optional van der Waals table contained in a `SinglefileData`.",
        )
        spec.input_namespace(
            "pseudos",
            valid_type=(LegacyUpfData, UpfData),
            dynamic=True,
            required=True,
            help="A mapping of `UpfData` nodes onto the kind name to which they should apply.",
        )
        spec.input("kpoints", valid_type=orm.KpointsData, help="kpoint mesh or kpoint path")
        spec.input(
            "hubbard_file",
            valid_type=orm.SinglefileData,
            required=False,
            help="SinglefileData node containing the output Hubbard parameters from a HpCalculation",
        )
