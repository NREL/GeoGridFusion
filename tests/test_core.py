import pytest
import geogridfusion

# @pytest.fixture(scope="module")
# def connect():
#     conn = geogridfusion.start()
#     yield conn
#     conn.close()

# def test_uninitialized_init():
#     """we can capture output"""

#     geogridfusion.initdb()


### if we are local we want to use the default start, other wise we want to monkeypatch test_start()

def test_version():
    conn = geogridfusion.start()

    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        print("PostgreSQL version:", cur.fetchone()[0])

        cur.execute("select extversion from pg_extension where extname = 'postgis';")
        version = cur.fetchone()[0]
        print("Postgis version:", version)

        assert version is not None


def test_initialize_tables():
    """
    this auto-initalizes tables for us 
    """

    # auto-initialize-tables for us
    conn = geogridfusion.start()

    with conn.cursor() as cur:

        cur.execute("""
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';
        """)
        result = cur.fetchall()

    flat = set()

    for tup in result:
        for string in tup:
            flat.add(string)

    assert (
        "files" in flat and
        "meta" in flat
    )


def test_sources():
    conn = geogridfusion.start()

    # nothing stored yet
    result = geogridfusion.sources(conn=conn)

    assert result == {}
