from pathlib import Path
import os
from shutil import which

REPO_NAME = __name__
GEOGRIDFUSION_DIR = Path(__file__).parent
WATCHDOG_PATH = GEOGRIDFUSION_DIR / "watchdog.py"

_pg_path = which("postgres")
POSTGRES_EXE_PATH = (
    Path(_pg_path) if _pg_path else None
)  # Safely handle missing executable

if POSTGRES_EXE_PATH is None:
    print("Postgres not found on path.")

if os.name == "nt":
    DATA_DIR = Path(os.getenv("APPDATA")) / "pgsql" / "geogridfusion-data"
else:
    DATA_DIR = Path.home() / ".config" / "pgsql" / "geogridfusion-data"
