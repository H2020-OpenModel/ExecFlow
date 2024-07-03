"""
Testing the functionalities of premod plugin
"""

from __future__ import annotations

from pathlib import Path

import dlite

from execflow.data.setup_dlite import setup_dlite

setup_dlite()


testdir = Path(__file__).resolve().parent.parent.parent
pkgdir = testdir.parent
sampledir = testdir / "samples"


# if True:
def test_singlefilenode_plugin():
    """
    The using the singlefile_coverter
    """

    dlite.storage_path.append(sampledir / "DLiteDataModelReaction.json")
    sample = sampledir / "dlite_instance_reaction.json"

    instance = dlite.Instance.from_location("singlefiledatanode", sample, options="parse_driver=json")

    assert instance.properties.keys() == {
        "reactants",
        "products",
        "reactant_stoichiometric_coefficient",
        "product_stoichiometric_coefficient",
        "energy",
    }
