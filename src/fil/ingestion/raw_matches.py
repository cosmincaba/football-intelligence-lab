import json

import psycopg
from psycopg.types.json import Jsonb

from fil.ingestion.hashing import sha256_of_bytes

def upsert_raw_match(
    conn: psycopg.Connection,
    source_file_path: str,
    raw_bytes: bytes,       
) -> str:
    """Insert, update, or skip a raw match JSON document.

    Returns 'inserted', 'updated', or 'skipped'.
    The caller owns the transaction.
    """

    # 1. Calculate SHA-256 from the original bytes
    content_hash = sha256_of_bytes(raw_bytes)

    # 2. Parse the raw bytes into Python object
    payload = json.loads(raw_bytes)

    # 3. Insert or update the PostgreSQL record
    query = """
        INSERT INTO raw.matches_json (
            source_file_path,
            payload,
            content_hash
        )
        VALUES (
            %(source_file_path)s,
            %(payload)s,
            %(content_hash)s
        )
        ON CONFLICT (source_file_path)
        DO UPDATE SET
            payload = EXCLUDED.payload,
            content_hash = EXCLUDED.content_hash,
            updated_at = NOW()
        WHERE raw.matches_json.content_hash
              IS DISTINCT FROM EXCLUDED.content_hash
        RETURNING (xmax = 0) AS was_inserted;
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            {
                "source_file_path": source_file_path,
                "payload": Jsonb(payload),
                "content_hash": content_hash,
            },
        )

        result = cur.fetchone()

    if result is None:
        return "skipped"

    if result[0]:
        return "inserted"

    return "updated"