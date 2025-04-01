from psycopg2.extensions import connection

def initialize_tables(conn: connection) -> None:
    """initalize postgresql tables with GeoGridFusion schema"""

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            latitude DOUBLE PRECISION NOT NULL, 
            longitude DOUBLE PRECISION NOT NULL, 
            file_path TEXT, -- nullable so we can determine filepath after insert based on id
            coords geometry(Point, 4326) GENERATED ALWAYS AS (
                ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
            ) STORED,
            size BIGINT NOT NULL,
            partial_hash TEXT NOT NULL,
            full_hash TEXT NOT NULL,

            UNIQUE(full_hash)
        );
        """
    )

    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_coords ON files USING GIST(coords);")
    cur.execute("CREATE INDEX IF NOT EXISTS fast_match ON files (size, partial_hash);")

    cur.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                id INTEGER PRIMARY KEY REFERENCES files(id),
                length      INT,
                source_name TEXT,
                source_res  TEXT,
                tmy         BOOL,
                tz_offset   TEXT,
                altitude    FLOAT,
                wind_height FLOAT
                -- OTHER
            );
            """
        )

    cur.execute("CREATE INDEX IF NOT EXISTS idx_source_name ON meta (source_name);")
    #cur.execute("CREATE INDEX IF NOT EXISTS idx_source_res ON meta (source_res);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tmy ON meta (tmy);")

    conn.commit()
    cur.close()