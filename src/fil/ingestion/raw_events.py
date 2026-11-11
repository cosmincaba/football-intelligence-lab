import json

from psycopg.types.json import Jsonb

from fil.ingestion.hashing import sha256_of_bytes

def upsert_raw_events(
    conn,
    match_id: int,
    source_file_path: str,
    raw_bytes: bytes,
) -> str:
    """
    Insert, update or skip a StatsBomb events file.

    Returns:
        "inserted" - new source file
        "updated"  - existing file with changed content
        "skipped"  - existing file with unchanged content

    Transaction management belongs to the caller.
    """

    # Parse and validate the downloaded JSON
    payload = json.loads(raw_bytes)

    if not isinstance(payload, list):
        raise ValueError(
            "Expected a JSON array of StatsBomb events."
        )

    # Calculate SHA-256 hash of the original bytes
    content_hash = sha256_of_bytes(raw_bytes)

    # Insert or conditionally update

    sql = """
        INSERT INTO raw.events_json (
            source_file_path,
            match_id,
            payload,
            content_hash
        )
        VALUES (%s, %s, %s, %s)

        ON CONFLICT (source_file_path)
        DO UPDATE SET
            match_id = EXCLUDED.match_id,
            payload = EXCLUDED.payload,
            content_hash = EXCLUDED.content_hash,
            updated_at = clock_timestamp()

        WHERE raw.events_json.content_hash
              IS DISTINCT FROM EXCLUDED.content_hash
           OR raw.events_json.match_id
              IS DISTINCT FROM EXCLUDED.match_id

        RETURNING (xmax = 0) AS was_inserted;
    """

    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                source_file_path,
                match_id,
                Jsonb(payload),
                content_hash,
            ),
        )

        result = cur.fetchone()

    if result is None:
        return "skipped"

    return "inserted" if result[0] else "updated"

