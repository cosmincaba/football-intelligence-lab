
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from fil.ingestion.raw_matches import upsert_raw_match

# Load credentials from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

# Use the same source path and bytes for both calls
source_path = "tests/idempotency_check.json"

original_bytes = b'{"match_id": 123, "home_team": "Argentina"}'
modified_bytes = b'{"match_id": 123, "home_team": "France"}'

print("Connecting to PostgreSQL...", flush=True)

with psycopg.connect(
    host="127.0.0.1",
    port=os.getenv("POSTGRES_PORT", "5432"),
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    connect_timeout=5,
) as conn:

    print("Connected successfully!", flush=True)

    # Start with a clean test record
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM raw.matches_json WHERE source_file_path = %s",
            (source_path,),
        )
    conn.commit()

    # First ingestion
    first_result = upsert_raw_match(
        conn,
        source_path,
        original_bytes,
    )   
    conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT updated_at
            FROM raw.matches_json
            WHERE source_file_path = %s
            """,
            (source_path,),
        )
        first_updated_at = cur.fetchone()[0]

    print("First ingestion:", first_result)
    print("First updated_at:", first_updated_at)

    # Second ingestion
    second_result = upsert_raw_match(
        conn,
        source_path,
        modified_bytes,
    )
    conn.commit()

    # Third ingestion
    third_result = upsert_raw_match(
        conn,
        source_path,
        modified_bytes,
    )
    conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT updated_at, COUNT(*) OVER ()
            FROM raw.matches_json
            WHERE source_file_path = %s
            """,
            (source_path,),
        )
        second_updated_at, row_count = cur.fetchone()

    print("Second ingestion:", second_result)
    print("Second updated_at:", second_updated_at)
    print("Third ingestion:", third_result)
    print("Rows for source path:", row_count)

    # Assertions
    assert first_result == "inserted"
    assert second_result == "updated"
    assert third_result == "skipped"

    print("SUCCESS: INSERT -> UPDATE -> SKIP verified!")
