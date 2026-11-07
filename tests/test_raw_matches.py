
import os
from uuid import uuid4

import psycopg
from dotenv import load_dotenv

from fil.ingestion.raw_matches import upsert_raw_match


def test_upsert_raw_match_insert_skip_update():
    load_dotenv()

    # Unique path prevents conflicts with existing test data
    source_path = f"tests/{uuid4()}.json"

    original_bytes = b'{"match_id": 123, "home_team": "Argentina"}'
    modified_bytes = b'{"match_id": 123, "home_team": "France"}'

    conn = psycopg.connect(
        host="127.0.0.1",
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )

    try:
        # First call: INSERT
        first_result = upsert_raw_match(
            conn, source_path, original_bytes
        )
        assert first_result == "inserted"

        # Second call: SKIP (same content)
        second_result = upsert_raw_match(
            conn, source_path, original_bytes
        )
        assert second_result == "skipped"

        # Third call: UPDATE (changed content)
        third_result = upsert_raw_match(
            conn, source_path, modified_bytes
        )
        assert third_result == "updated"

        # Verify stored data inside the transaction
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT payload
                FROM raw.matches_json
                WHERE source_file_path = %s
                """,
                (source_path,),
            )
            stored_payload = cur.fetchone()[0]

        assert stored_payload["home_team"] == "France"

    finally:
        # Undo all changes, even if an assertion fails
        conn.rollback()
        conn.close()
