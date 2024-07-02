from __future__ import annotations

from pathlib import Path

import dlite

# This seems to append entities dir to dlite.storage_path
from execflow.data.singlefile_converter import singlefile_converter

testdir = Path(__file__).resolve().parent.parent.parent
pkgdir = testdir.parent
sampledir = testdir / "samples"


# Basic
DataModel = dlite.get_instance("http://onto-ns.com/meta/2.0/core.singlefile")


# Step 2
sample = sampledir / "dlite_instance_reaction.json"
with Path.open(sample, "rb") as f:
    content = f.read()

singlefileinst = DataModel(dimensions=(len(content),))
singlefileinst.content = content


# save the instance as a file to use the singlefiledatanode plugin directly
singlefileinst.save("yaml", "instance.yaml", options="mode=w")
# load it back inn
# inst0 = dlite.Instance.from_location("json",
#                                      "instance.json")


# step 3, load the instance directly from file
dlite.storage_path.append(sampledir / "DLiteDataModelReaction.json")
print(pkgdir / "execflow" / "data" / "dlite_plugins")
dlite.python_storage_plugin_path.append(pkgdir / "execflow" / "data" / "dlite_plugins")
# load with json after havin made singlenodefile available
inst1 = dlite.Instance.from_location("yaml2", "instance.yaml")


inst2 = dlite.Instance.from_location("singlefiledatanode", "instance.json", options="driver=json")


# Step 4 use the singelfile_converter
dlite.storage_path.append(sampledir / "DLiteDataModelReaction.json")
instance_from_singlefiledatanode = singlefile_converter(singlefileinst, parse_driver="json", options="mode=r")

direct_instance = dlite.Instance.from_location("json", sample, options="mode=r")

assert instance_from_singlefiledatanode.properties.keys() == direct_instance.properties.keys()
