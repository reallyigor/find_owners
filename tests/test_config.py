"""
Tests for the config module.
"""

import os
from unittest.mock import patch

import pytest

from owners_finder.config import get_api_base_url, get_api_headers, get_perplexity_api_key, get_request_timeout


def test_get_perplexity_api_key_success():
    """Test getting API key when it's set."""
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-api-key"}):
        assert get_perplexity_api_key() == "test-api-key"


def test_get_perplexity_api_key_missing():
    """Test getting API key when it's not set."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="PERPLEXITY_API_KEY environment variable is required"):
            get_perplexity_api_key()


def test_get_api_base_url_default():
    """Test getting API base URL with default value."""
    with patch.dict(os.environ, {}, clear=True):
        assert get_api_base_url() == "https://api.perplexity.ai"


def test_get_api_base_url_custom():
    """Test getting API base URL with custom value."""
    custom_url = "https://custom.api.url"
    with patch.dict(os.environ, {"PERPLEXITY_API_BASE_URL": custom_url}):
        assert get_api_base_url() == custom_url


def test_get_request_timeout_default():
    """Test getting request timeout with default value."""
    with patch.dict(os.environ, {}, clear=True):
        assert get_request_timeout() == 30


def test_get_request_timeout_custom():
    """Test getting request timeout with custom value."""
    with patch.dict(os.environ, {"REQUEST_TIMEOUT": "60"}):
        assert get_request_timeout() == 60


def test_get_api_headers():
    """Test getting API headers."""
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
        headers = get_api_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-key"
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"


def test_get_api_headers_missing_key():
    """Test getting API headers when key is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            get_api_headers()
