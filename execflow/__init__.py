__version__ = "0.2.0"

from pathlib import Path
import dlite


# Paths
thisdir = Path(__file__).resolve().parent
entitydir = thisdir / "entities"

# Add data models to the DLite search path
dlite.storage_path.append(entitydir)

