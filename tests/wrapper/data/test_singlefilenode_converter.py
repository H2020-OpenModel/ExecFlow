"""
Testing the functionalities of premod plugin
"""

from __future__ import annotations

from pathlib import Path

import dlite

from execflow.data.singlefile_converter import singlefile_converter

testdir = Path(__file__).resolve().parent.parent.parent
pkgdir = testdir.parent
sampledir = testdir / "samples"


# if True:
def test_singlefilenode_using_converter_w_options():
    """
    The using the singlefile_coverter
    """

    dlite.storage_path.append(sampledir / "DLiteDataModelReaction.json")
    sample = sampledir / "dlite_instance_reaction.json"
    # Create a singlefiledatanode instance witht the content equal
    # to the file generated by Abaqus

    # Note that if getting this instance does not work it might be because
    # the sintef entities-service is not running.
    # This can be checked by pasting the url in the browser
    DataModel = dlite.get_instance("http://onto-ns.com/meta/2.0/core.singlefile")
    with Path.open(sample, "rb") as f:
        content = f.read()

    singlefileinst = DataModel(dimensions=(len(content),))
    singlefileinst.content = content
    assert singlefileinst.properties.keys() == {"content", "filename"}

    instance_from_singlefiledatanode = singlefile_converter(singlefileinst, parse_driver="json", options="mode=r")

    assert instance_from_singlefiledatanode.properties.keys() == {
        "reactants",
        "products",
        "reactant_stoichiometric_coefficient",
        "product_stoichiometric_coefficient",
        "energy",
    }


def test_singlefilenode_using_converter_no_options():
    """
    The using the singlefile_coverter
    """

    dlite.storage_path.append(sampledir / "DLiteDataModelReaction.json")
    sample = sampledir / "dlite_instance_reaction.json"
    # Create a singlefiledatanode instance witht the content equal
    # to the file generated by Abaqus

    # Note that if getting this instance does not work it might be because
    # the sintef entities-service is not running.
    # This can be checked by pasting the url in the browser
    DataModel = dlite.get_instance("http://onto-ns.com/meta/2.0/core.singlefile")
    with Path.open(sample, "rb") as f:
        content = f.read()

    singlefileinst = DataModel(dimensions=(len(content),))
    singlefileinst.content = content
    assert singlefileinst.properties.keys() == {"content", "filename"}

    instance_from_singlefiledatanode = singlefile_converter(singlefileinst, parse_driver="json")

    assert instance_from_singlefiledatanode.properties.keys() == {
        "reactants",
        "products",
        "reactant_stoichiometric_coefficient",
        "product_stoichiometric_coefficient",
        "energy",
    }
