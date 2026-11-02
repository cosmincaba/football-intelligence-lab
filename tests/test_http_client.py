
from unittest.mock import Mock, patch

import pytest
import requests

from fil.ingestion.http_client import fetch_bytes


@patch("fil.ingestion.http_client.requests.get")
def test_fetch_bytes_success(mock_get):
    mock_response = Mock()
    mock_response.content = b'{"match_id": 123}'
    mock_get.return_value = mock_response

    result = fetch_bytes("https://example.com/match.json")

    assert result == b'{"match_id": 123}'
    mock_get.assert_called_once_with(
        "https://example.com/match.json",
        timeout=30,
    )
    mock_response.raise_for_status.assert_called_once()


@patch("fil.ingestion.http_client.requests.get")
def test_fetch_bytes_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("404 Not Found")
    )
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        fetch_bytes("https://example.com/missing.json")


@patch("fil.ingestion.http_client.requests.get")
def test_fetch_bytes_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout(
        "Request timed out"
    )

    with pytest.raises(requests.exceptions.Timeout):
        fetch_bytes("https://example.com/slow.json")
