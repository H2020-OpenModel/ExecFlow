"""
Dlite plugin to convert between DLite instances or files and AiiDA single file datanode.
To be included in ExecFlow.

"""

from __future__ import annotations

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

        self.driver, self.options = self.set_options(options)
        self.location = location

    def load(self, id=None) -> dlite.Instance:  # noqa: ARG002
        """
        Load a state file and return it as a DLite instance

        Returns:
            A DLite Instance corresponding to the given filename.

        """
        return dlite.Instance.from_location(self.driver, self.location, options=self.options)

    @classmethod
    def from_bytes(cls, buffer, id=None, options=None):  # noqa: ARG003
        """
        Arguments:
            buffer: Bytes, id=None of bytearray to load instance from.
            id: ID of instance to load. May be omitted if `buffer`
                only holds one instance.
        Returns:
           New instance

        """
        driver, options = cls.set_options(options)

        return dlite.Instance.from_bytes(driver, buffer, options=options)

    @staticmethod
    def set_options(optionsstring):
        options = Options(optionsstring, defaults="driver=json")
        driver = options.pop("driver")
        if options:
            opts = [f"{key}={value}" for key, value in options.items()]
            optionsfordriver = ";".join(opts)
        else:
            optionsfordriver = None

        return driver, optionsfordriver
