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


def singlefile_converter(singlefile_instance, parse_driver="json", options=None):
    """The converter function

    Argsuments:
        singlefile_instance: an AiiDA singlefiledatanode instance
        parse_driver: the driver to be used to parse the buffer which is
            the value of the "content" property of the singlefiledatanode instance.
            This is the driver that would be used to parse the content if parsed directly
            from a file.
        options: the options to be passed to the driver that will parse the buffer.

    Returns:
        An instance of DLite instance that is parsed from the buffer of the singlefiledatanode instance.
    """
    setup_dlite()
    print("--------------")
    print(dlite.python_storage_plugin_path)
    print("----------------")
    if singlefile_instance.meta.uri != "http://onto-ns.com/meta/2.0/core.singlefile":
        raise ValueError(f"Expected a singlefile instance, got {singlefile_instance.meta.uri}")
    buffer = singlefile_instance.content.tobytes()
    # save buffer to temporary file and load it as a DLite instance
    # use a temporary directory
    parse_options = ";".join([f"driver={parse_driver}", f"{options}"]) if options else f"driver={parse_driver}"
    try:
        return dlite.Instance.from_bytes(
            driver="singlefiledatanode", buffer=singlefile_instance.content.tobytes(), options=parse_options
        )

    # Versions of DLite-Pyhon<0.5.21 do not allow for options in the
    # to_bytes and from_bytes class methods in the plugins.
    # Many plugins might also not have a from_bytes method.
    except (
        dlite.DLiteTypeError,
        TypeError,
        Exception,  # if from_bytes() in parse_driver does not accept options
        dlite.DLiteAttributeError,  # if parse driver does not support from_bytes
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = temp_dir + "/temp_file"
            with Path.open(Path(temp_file), "wb") as f:
                f.write(buffer)
            return dlite.Instance.from_location(driver="singlefiledatanode", location=temp_file, options=parse_options)
