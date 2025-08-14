import subprocess
import psycopg2
import time
import sys
import os

import geogridfusion


def wait_for_postgres(timeout=30, host="localhost", password: str = None):
    # errors that we may encounter in the startup process
    RECOVERABLE_ERRORS = [
        "starting up",
        "server closed the connection",
        "the database system is starting up",
        "the database system is shutting down",
        "Connection refused",
    ]

    extra = {}
    if password is not None:
        extra = {"password": password}

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = psycopg2.connect(
                dbname="postgres", user="postgres", host=host, port="5432", **extra
            )
            print(
                "PostgreSQL connection established after "
                f"{time.time() - start_time:.2f} seconds."
            )
            return conn
        except psycopg2.OperationalError as e:
            if any(msg in str(e) for msg in RECOVERABLE_ERRORS):
                time.sleep(1)
            else:
                raise e
    raise TimeoutError("PostgreSQL did not startup in time.")


def start():
    """
    Start Postgresql server, start watchdog and return a connection.
    Initializes PostgreSQL if needed (init_db).

    Postgres and PostGIS must already be installed in the environment.
    Follow installation instructions on github or ReadTheDocs.
    """

    geogridfusion.initdb()

    if os.name == "nt":
        start_windows()
    elif os.name == "posix":
        start_posix()
    else:
        raise NotImplementedError(f"geogridfusion not available on os: {os.name} ")

    conn = wait_for_postgres()
    cur = conn.cursor()

    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis');")
    exists = cur.fetchone()[0]

    if exists:
        print("postgis already installed")
    else:
        try:
            print("attempting to create postgis extension")
            cur.execute("CREATE EXTENSION postgis;")
            conn.commit()
        except Exception as e:
            print(f"Failed to create PostGIS extension: {e}")
            conn.rollback()
            raise e

    cur.close()

    geogridfusion.initialize_tables(conn=conn)

    return conn


def _start_test():
    for i in range(5):
        print("IN START_TEST FUNCTION")

    conn = wait_for_postgres(host="localhost", password="postgres")

    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()

    geogridfusion.initialize_tables(conn=conn)

    return conn


def start_posix():
    print("Starting Postgres subprocess...")

    subprocess.Popen(
        [
            sys.executable,
            str(geogridfusion.WATCHDOG_PATH),
            str(os.getpid()),
            "postgres",
            "-D",
            geogridfusion.DATA_DIR,
        ],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def start_windows():
    print("Starting Postgres subprocess...")

    # we be using pg_ctl to do this instead
    DETACHED_PROCESS = 0x00000008  # windows quirk
    subprocess.Popen(
        [
            sys.executable,
            str(geogridfusion.WATCHDOG_PATH),
            str(os.getpid()),
            "postgres",
            "-D",
            geogridfusion.DATA_DIR,
        ],
        creationflags=DETACHED_PROCESS,  # windows quirk
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# def start_win():
#     """
#     initalize postgresql if needed, start server and watchdog and return a connection

#     postgres must be installed as instructions show in documenation for reliability.
#     """

#     geogridfusion.initdb()

#     print("Starting Postgres subprocess...")

#     # we be using pg_ctl to do this instead
#     DETACHED_PROCESS = 0x00000008 # windows quirk
#     subprocess.Popen([
#         sys.executable,
#         str(geogridfusion.WATCHDOG_PATH),
#         str(os.getpid()),
#         "postgres",
#         "-D",
#         geogridfusion.DATA_DIR
#     ],
#     creationflags=DETACHED_PROCESS, # windows quirk
#     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL # windows quirk
#     )

#     conn = wait_for_postgres()
#     cur = conn.cursor()

# cur.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis');")
#     exists = cur.fetchone()[0]

#     if exists:
#         print("postgis already installed")
#     else:
#         print("attempting to create postgis extension")
#         cur.execute("CREATE EXTENSION postgis;")
#         conn.commit()

#     cur.close()

#     return conn
