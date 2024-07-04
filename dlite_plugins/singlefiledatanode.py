"""
Dlite plugin to convert between DLite instances or files and AiiDA single file datanode.
To be included in ExecFlow.

"""

from __future__ import annotations

import json

import dlite
from dlite.options import Options


class singlefiledatanode(dlite.DLiteStorageBase):
    """General description of the Python storage plugin."""

    def open(self, location, options=None):
        """Open storage.

        Arguments:
            location: location of the file
            options: The options define which driver should be
                used to parse the content of the singlefiledatanode,
                and additional options to this driver.
                e.g. (options="driver=json;mode=w")
        """

        self.options = Options(options, defaults="driver=json")
        self.location = location

    def load(self, id=None) -> dlite.Instance:  # noqa: ARG002
        """
        Load a state file and return it as a DLite instance

        Returns:
            A DLite Instance corresponding to the given filename.

        """
        return dlite.Instance.from_location(self.driver, self.location, options=self.options)

    @classmethod
    def from_bytes(cls, buffer, id=None):  # noqa: ARG003
        """
        From the content of the Abaqus output file
        generate documented DLite output instance of
        http://www.sintef.no/calm/0.1/AbaqusDeformationHistory

        Arguments:
            buffer: Bytes, id=None of bytearray to load instance from.
            id: ID of instance to load. May be omitted if `buffer`
                only holds one instance.
        Returns:
           New instance

        """
        return cls.create_instance(buffer)

    @staticmethod
    def create_instance(content):
        """
        read a state file and populate a DLite instance base on it
        """
        # read the file as a dictionary
        dict_output = json.loads(content)

        return dlite.Instance.from_dict(dict_output)
