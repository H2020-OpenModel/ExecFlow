"""
Dlite plugin to convert between DLite instances or files and AiiDA single file datanode.
To be included in ExecFlow.

"""

import dlite
import json
from dlite.options import Options


class singlefiledatanode(dlite.DLiteStorageBase):
    """General description of the Python storage plugin."""

    def open(self, location, options=None):
        """Open storage.

        Arguments:
            location: Path where the output file from Abaqus will be written
            options: Additional options for this storage driver.
        """
        self.options = Options(options, defaults="driver=json")
        self.location = location

    def load(self, id=None) -> dlite.Instance:
        """
        Load a state file and return it as a DLite instance

        Returns:
            A DLite Instance corresponding to the given filename.

        """
        inst = dlite.Instance.from_location(self.options.driver, self.location)

        return inst

    @classmethod
    def from_bytes(cls, buffer, id=None):
        """
        From the content of the Abaqus output file
        generate documented DLite output instance of
        http://www.sintef.no/calm/0.1/AbaqusDeformationHistory

        Arguments:
            buffer: Bytes of bytearray to load instance from.
            id: ID of instance to load. May be omitted if `buffer`
                only holds one instance.
        Returns:
           New instance

        """
        inst = cls.create_instance(buffer)
        return inst

    ## add the save function
    @staticmethod
    def create_instance(content):
        """
        read a state file and populate a DLite instance base on it
        """
        # read the file as a dictionary
        dict_output = json.loads(content)

        inst = dlite.Instance.from_dict(dict_output)
        return inst
