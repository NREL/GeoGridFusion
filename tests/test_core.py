import pytest
import geogridfusion

@pytest.fixture(scope="module")
def connect():
    conn = geogridfusion.start()
    yield conn
    conn.close()

def test_init_db():
    ...

def test_initialize_tables():
    ...

def test_sources():
    ...
