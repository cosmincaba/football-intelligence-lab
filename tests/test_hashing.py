from fil.ingestion.hashing import sha256_of_bytes

def test_same_bytes_same_hash():
    data = b"football"

    hash_1 = sha256_of_bytes(data)
    hash_2 = sha256_of_bytes(data)

    assert hash_1 == hash_2

def test_one_byte_change_different_hash():
    original = b"football"
    modified = b"footbalL"

    assert sha256_of_bytes(original) != sha256_of_bytes(modified)