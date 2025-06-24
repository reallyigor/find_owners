"""
Tests for the main module.
"""

import json
import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from owners_finder.main import find_company_owners, main, save_to_json


@patch("owners_finder.main.parse_company_info")
@patch("owners_finder.main.clean_response_content")
@patch("owners_finder.main.extract_content_from_response")
@patch("owners_finder.main.call_perplexity_api")
@patch("owners_finder.main.create_company_prompt")
def test_find_company_owners_success(mock_prompt, mock_api, mock_extract, mock_clean, mock_parse):
    """Test successful company owners finding."""
    # Setup mocks
    mock_prompt.return_value = "test prompt"
    mock_api.return_value = {"choices": [{"message": {"content": "test response"}}]}
    mock_extract.return_value = "test response"
    mock_clean.return_value = "cleaned response"
    mock_parse.return_value = {
        "company_name": "Test Corp",
        "website": "https://test.com",
        "description": "A test company",
        "owners": [{"name": "John Doe", "title": "CEO"}],
    }

    result = find_company_owners("https://test.com")

    assert result["company_name"] == "Test Corp"
    assert result["website"] == "https://test.com"
    assert len(result["owners"]) == 1

    # Verify all functions were called
    mock_prompt.assert_called_once_with("https://test.com")
    mock_api.assert_called_once_with("test prompt")
    mock_extract.assert_called_once()
    mock_clean.assert_called_once_with("test response")
    mock_parse.assert_called_once_with("cleaned response", "https://test.com")


def test_find_company_owners_invalid_url():
    """Test finding company owners with invalid URL."""
    with pytest.raises(ValueError, match="Invalid URL"):
        find_company_owners("not-a-url")


@patch("owners_finder.main.call_perplexity_api")
def test_find_company_owners_api_error(mock_api):
    """Test finding company owners when API fails."""
    mock_api.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="Failed to find company owners"):
        find_company_owners("https://test.com")


def test_save_to_json():
    """Test saving data to JSON file."""
    data = {"company_name": "Test Corp", "website": "https://test.com", "description": "A test company", "owners": []}

    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            filename = save_to_json(data)

            # Check file was created
            assert os.path.exists(filename)
            assert filename == "test_corp_info.json"

            # Check file contents
            with open(filename, "r") as f:
                loaded_data = json.load(f)

            assert loaded_data == data

        finally:
            os.chdir(original_cwd)


def test_save_to_json_custom_filename():
    """Test saving data with custom filename."""
    data = {"company_name": "Custom Corp"}

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            filename = save_to_json(data, "custom_name.json")

            assert os.path.exists(filename)
            assert filename == "custom_name.json"

        finally:
            os.chdir(original_cwd)


def test_save_to_json_clean_filename():
    """Test saving data with special characters in company name."""
    data = {"company_name": "Test/Corp & Co.!"}

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            filename = save_to_json(data)

            # Should clean special characters
            assert filename == "testcorp__co_info.json"
            assert os.path.exists(filename)

        finally:
            os.chdir(original_cwd)


@patch("sys.argv", ["main.py", "https://test.com"])
@patch("owners_finder.main.find_company_owners")
@patch("owners_finder.main.save_to_json")
@patch("builtins.print")
def test_main_success(mock_print, mock_save, mock_find):
    """Test successful main function execution."""
    # Setup mocks
    mock_find.return_value = {
        "company_name": "Main Test Corp",
        "website": "https://test.com",
        "description": "A main test company",
        "owners": [{"name": "Main Owner", "title": "CEO", "ownership_percentage": "100%"}],
        "industry": "Technology",
        "founded_year": "2020",
        "headquarters": "Test City",
    }
    mock_save.return_value = "main_test_corp_info.json"

    # Should not raise any exceptions
    try:
        main()
    except SystemExit:
        pass  # Expected for successful completion

    # Verify functions were called
    mock_find.assert_called_once_with("https://test.com")
    mock_save.assert_called_once()


@patch("sys.argv", ["main.py"])
@patch("sys.exit")
@patch("builtins.print")
def test_main_no_args(mock_print, mock_exit):
    """Test main function with no arguments."""
    try:
        main()
    except SystemExit:
        pass

    mock_exit.assert_called_with(1)
    # Should print usage message
    mock_print.assert_called()


@patch("sys.argv", ["main.py", "invalid-url"])
@patch("owners_finder.main.find_company_owners")
@patch("sys.exit")
@patch("builtins.print")
def test_main_invalid_url(mock_print, mock_exit, mock_find):
    """Test main function with invalid URL."""
    mock_find.side_effect = ValueError("Invalid URL")

    main()

    mock_exit.assert_called_with(1)


@patch("sys.argv", ["main.py", "https://test.com"])
@patch("owners_finder.main.find_company_owners")
@patch("sys.exit")
@patch("builtins.print")
def test_main_api_error(mock_print, mock_exit, mock_find):
    """Test main function with API error."""
    mock_find.side_effect = Exception("API Error")

    main()

    mock_exit.assert_called_with(1)
