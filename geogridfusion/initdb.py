"""
setup module to initialize db if it does not exist
"""

import os
import subprocess
from geogridfusion.config import DATA_DIR


def initdb():
    if os.path.exists(DATA_DIR):
        return

    # The passwordless user (usually 'postgres') for initdb
    username = "postgres"

    # Run initdb using subprocess
    try:
        subprocess.run(
            [
                "initdb",
                "-D",
                DATA_DIR,
                "-U",
                username,
            ],
            check=True,
        )
        print(f"Successfully initialized PostgreSQL cluster at {DATA_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"initdb failed: {e}")
