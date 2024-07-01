"""Setup DLite search paths"""
from pathlib import Path

import dlite


def setup_dlite():
    """Setup DLite search paths for datamodels and storage plugins."""
    print(dlite.python_storage_plugin_path)
    pkgdir = Path(__file__).resolve().parent
    dlite.python_storage_plugin_path.append(pkgdir / "dlite_plugins")
    print(dlite.python_storage_plugin_path)
