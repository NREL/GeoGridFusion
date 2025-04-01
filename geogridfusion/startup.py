import subprocess
import psycopg2
import time
import sys
import os
from pathlib import Path

import geogridfusion

def wait_for_postgres(timeout=30):

    # errors that we may encounter in the startup process
    RECOVERABLE_ERRORS = [
        "starting up", 
        "server closed the connection", 
        "the database system is starting up", 
        "the database system is shutting down",
        "Connection refused"
    ]

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = psycopg2.connect(
                dbname="postgres", user="postgres", host="localhost", port="5432"
            )
            print(f"PostgreSQL connection established after {time.time() - start_time:.2f} seconds.")
            return conn
        except psycopg2.OperationalError as e:
            if any(msg in str(e) for msg in RECOVERABLE_ERRORS):
                time.sleep(1)
            else:
                raise e 
    raise TimeoutError("PostgreSQL did not startup in time.")

def start():
    if os.name == 'nt':
        return start_win()
    else:
        raise NotImplementedError("only implemented for windows.")

def start_win():
    """
    initalize postgresql if needed, start server and watchdog and return a connection

    postgres must be installed as instructions show in documenation for reliability.
    """

    geogridfusion.initdb()

    print("Starting Postgres subprocess...")

    # we be using pg_ctl to do this instead
    DETACHED_PROCESS = 0x00000008 # windows quirk
    subprocess.Popen([
        sys.executable, 
        str(geogridfusion.WATCHDOG_PATH), 
        str(os.getpid()), 
        "postgres", 
        "-D", 
        geogridfusion.DATA_DIR
    ], 
    creationflags=DETACHED_PROCESS, # windows quirk
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL # windows quirk
    )

    conn = wait_for_postgres()
    cur = conn.cursor()

    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis');")
    exists = cur.fetchone()[0]

    if exists:
        print("postgis already installed")
    else:
        print("attempting to create postgis extension")
        cur.execute("CREATE EXTENSION postgis;")
        conn.commit() 

    cur.close()

    return conn

