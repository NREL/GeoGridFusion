import psycopg2
import time

import geogridfusion


def wait_for_postgres(
    timeout=30,
    dbname: str = "postgres",
    user: str = "postgres",
    host="localhost",
    password: str = "password",
    port: str = "5432",
):
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
                dbname=dbname,
                user=user,
                host=host,
                port=port,
                **extra,  # type: ignore
            )  # type: ignore
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
    raise TimeoutError("PostgreSQL did not connect in time.")


# def start():
#     """
#     Conenct to Postgresql server.
#     Initializes PostgreSQL if needed (init_db).

#     If postgres is not installed already, install it yourself, run `geogridfusion.run_container` or host it externally.

#     Follow installation instructions on github or ReadTheDocs.
#     """

#     conn = wait_for_postgres()
#     cur = conn.cursor()

#     cur.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis');")
#     exists = cur.fetchone()[0]

#     # this may not be required
#     if exists:
#         print("postgis already installed")
#     else:
#         try:
#             print("attempting to create postgis extension")
#             cur.execute("CREATE EXTENSION postgis;")
#             conn.commit()
#         except Exception as e:
#             print(f"Failed to create PostGIS extension: {e}")
#             conn.rollback()
#             raise e

#     cur.close()

#     geogridfusion.initialize_tables(conn=conn)

#     return conn


def _start_test():
    for i in range(5):
        print("IN START_TEST FUNCTION")

    conn = wait_for_postgres(host="localhost", password="postgres")

    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()

    geogridfusion.initialize_tables(conn=conn)

    return conn
