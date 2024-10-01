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


def test_singlefilenode_plugin_no_extra_options():
    """
    The using the singlefiledatanode plugin
    """

    dlite.storage_path.append(sampledir / "DLiteDataModelReaction.json")
    sample = sampledir / "dlite_instance_reaction.json"

    instance = dlite.Instance.from_location("singlefiledatanode", sample, options="driver=json")

    assert instance.properties.keys() == {
        "reactants",
        "products",
        "reactant_stoichiometric_coefficient",
        "product_stoichiometric_coefficient",
        "energy",
    }


def test_singlefilenode_plugin_w_options():
    """
    The using the singlefiledatanode plugin including extra options for
    the secondary driver.
    """

    dlite.storage_path.append(sampledir / "DLiteDataModelReaction.json")
    sample = sampledir / "dlite_instance_reaction.json"

    instance = dlite.Instance.from_location("singlefiledatanode", sample, options="driver=json;mode=r")

    assert instance.properties.keys() == {
        "reactants",
        "products",
        "reactant_stoichiometric_coefficient",
        "product_stoichiometric_coefficient",
        "energy",
    }


def test_singlefilenode_plugin_from_bytes():
    """
    The singlefiledatanode plugin with from_bytes is
    tested as part of the converter test.
    """
