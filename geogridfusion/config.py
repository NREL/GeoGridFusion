from pathlib import Path
import os

REPO_NAME = __name__
GEOGRIDFUSION_DIR = Path(__file__).parent

# run postgres-postgis container

# TODO: required?
if os.name == "nt":
    DATA_DIR = Path(os.getenv("APPDATA")) / "pgsql" / "geogridfusion-data"
else:
    DATA_DIR = Path.home() / ".config" / "pgsql" / "geogridfusion-data"

    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)
