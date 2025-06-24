"""
Tests for the api_client module.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from owners_finder.api_client import call_perplexity_api, create_company_prompt, extract_content_from_response


def test_create_company_prompt():
    """Test creating a company prompt."""
    url = "https://example.com"
    prompt = create_company_prompt(url)

    assert url in prompt
    assert "company_name" in prompt
    assert "description" in prompt
    assert "owners" in prompt
    assert "JSON" in prompt


@patch("owners_finder.api_client.requests.post")
@patch("owners_finder.api_client.get_api_headers")
@patch("owners_finder.api_client.get_api_base_url")
@patch("owners_finder.api_client.get_request_timeout")
def test_call_perplexity_api_success(mock_timeout, mock_base_url, mock_headers, mock_post):
    """Test successful API call."""
    # Mock configuration
    mock_timeout.return_value = 30
    mock_base_url.return_value = "https://api.perplexity.ai"
    mock_headers.return_value = {"Authorization": "Bearer test-key"}

    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    # Test the function
    result = call_perplexity_api("test prompt")

    assert result == {"choices": [{"message": {"content": "test response"}}]}
    mock_post.assert_called_once()


@patch("owners_finder.api_client.requests.post")
@patch("owners_finder.api_client.get_api_headers")
@patch("owners_finder.api_client.get_api_base_url")
@patch("owners_finder.api_client.get_request_timeout")
def test_call_perplexity_api_request_error(mock_timeout, mock_base_url, mock_headers, mock_post):
    """Test API call with request error."""
    # Mock configuration
    mock_timeout.return_value = 30
    mock_base_url.return_value = "https://api.perplexity.ai"
    mock_headers.return_value = {"Authorization": "Bearer test-key"}

    mock_post.side_effect = requests.RequestException("Connection error")

    with pytest.raises(requests.RequestException, match="API call failed"):
        call_perplexity_api("test prompt")


@patch("owners_finder.api_client.requests.post")
@patch("owners_finder.api_client.get_api_headers")
@patch("owners_finder.api_client.get_api_base_url")
@patch("owners_finder.api_client.get_request_timeout")
def test_call_perplexity_api_json_error(mock_timeout, mock_base_url, mock_headers, mock_post):
    """Test API call with JSON decode error."""
    # Mock configuration
    mock_timeout.return_value = 30
    mock_base_url.return_value = "https://api.perplexity.ai"
    mock_headers.return_value = {"Authorization": "Bearer test-key"}

    # Mock response with invalid JSON
    mock_response = Mock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    with pytest.raises(ValueError, match="Invalid JSON response"):
        call_perplexity_api("test prompt")


def test_extract_content_from_response_success():
    """Test extracting content from a valid response."""
    response = {"choices": [{"message": {"content": "This is the response content"}}]}

    content = extract_content_from_response(response)
    assert content == "This is the response content"


def test_extract_content_from_response_no_choices():
    """Test extracting content when no choices exist."""
    response = {"choices": []}

    with pytest.raises(ValueError, match="No choices found in API response"):
        extract_content_from_response(response)


def test_extract_content_from_response_no_message():
    """Test extracting content when no message exists."""
    response = {"choices": [{"not_message": "invalid"}]}

    with pytest.raises(ValueError, match="No content found in API response"):
        extract_content_from_response(response)


def test_extract_content_from_response_no_content():
    """Test extracting content when no content exists."""
    response = {"choices": [{"message": {"not_content": "invalid"}}]}

    with pytest.raises(ValueError, match="No content found in API response"):
        extract_content_from_response(response)


def test_extract_content_from_response_invalid_format():
    """Test extracting content from invalid response format."""
    response = {"invalid": "format"}

    with pytest.raises(ValueError, match="No choices found in API response"):
        extract_content_from_response(response)
