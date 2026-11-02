import requests

def fetch_bytes(url: str) -> bytes:

    response = requests.get(url, timeout=30)

    response.raise_for_status()

    return response.content