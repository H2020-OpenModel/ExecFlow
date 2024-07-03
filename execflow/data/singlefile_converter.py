"""
A converter function to be used by oteapi-dlite
to convert an AiiDA singlefiledatanode which
has as content a DLite instance serialised as json.
The AiiDA singlefile datanode is passed as
a http://onto-ns.com/meta/2.0/core.singlefile.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

import dlite

from execflow.data.setup_dlite import setup_dlite

setup_dlite()


def singlefile_converter(singlefile_instance, parse_driver="json", options=None):
    """The converter function"""

    if singlefile_instance.meta.uri != "http://onto-ns.com/meta/2.0/core.singlefile":
        raise ValueError(f"Expected a singlefile instance, got {singlefile_instance.meta.uri}")
    buffer = singlefile_instance.content.tobytes()
    # save buffer to temporary file and load it as a DLite instance
    # use a temporary directory

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = temp_dir + "/temp_file"
        with Path.open(Path(temp_file), "wb") as f:
            f.write(buffer)
        parse_options = (
            ";".join([f"driver={parse_driver}", f"options={options}"]) if options else f"driver={parse_driver}"
        )
        return dlite.Instance.from_location(driver="singlefiledatanode", location=temp_file, options=parse_options)
    # """The converter function"""
    # When it will be possible to pass options to the
    # from_bytes method of the DLite instance, the following
    # code can be used.
    # return dlite.Instance.from_bytes(
    #    driver='singlefiledatanode',
    #    buffer=singlefile_instance.content.tobytes(),
    #    options=parse_options
    # )
