from pathlib import Path
from getpass import getuser
import os
from shutil import which

REPO_NAME = __name__
GEOGRIDFUSION_DIR = Path(__file__).parent
WATCHDOG_PATH = GEOGRIDFUSION_DIR / "watchdog.py"
POSTGRES_EXE_PATH = Path(which('postgres'))

if os.name == "nt":
    DATA_DIR = Path(os.getenv("APPDATA")) / "pgsql" / "geogridfusion-data"
else:
    DATA_DIR = Path.home() / ".config" / "pgsql" / "geogridfusion-data"
