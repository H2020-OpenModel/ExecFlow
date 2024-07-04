"""Setup DLite search paths"""

from __future__ import annotations

from pathlib import Path

import dlite


def setup_dlite():
    """Setup DLite search paths for datamodels and storage plugins."""
    pkgdir = Path(__file__).resolve().parent.parent.parent
    dlite.python_storage_plugin_path.append(pkgdir / "dlite_plugins")
