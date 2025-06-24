"""
Tests for the parser module.
"""

import json

import pytest

from owners_finder.parser import (
    clean_response_content,
    extract_field_from_text,
    extract_json_from_text,
    extract_owners_from_text,
    parse_company_info,
    parse_text_response,
    structure_company_data,
)


def test_extract_json_from_text_code_block():
    """Test extracting JSON from code block."""
    text = """
    Here's the information:
    ```json
    {"company_name": "Test Corp", "description": "A test company"}
    ```
    That's all.
    """

    result = extract_json_from_text(text)
    assert result is not None
    assert result["company_name"] == "Test Corp"
    assert result["description"] == "A test company"


def test_extract_json_from_text_plain_json():
    """Test extracting JSON from plain text."""
    text = '{"company_name": "Plain Corp", "owners": []}'

    result = extract_json_from_text(text)
    assert result is not None
    assert result["company_name"] == "Plain Corp"
    assert result["owners"] == []


def test_extract_json_from_text_no_json():
    """Test when no JSON is found."""
    text = "This is just plain text without any JSON structure."

    result = extract_json_from_text(text)
    assert result is None


def test_structure_company_data():
    """Test structuring company data from JSON."""
    json_data = {
        "company_name": "Structured Corp",
        "description": "A structured company",
        "owners": [
            {"name": "John Doe", "title": "CEO", "ownership_percentage": "60%"},
            {"name": "Jane Smith", "title": "CTO"},
        ],
        "industry": "Technology",
        "founded_year": "2020",
        "headquarters": "San Francisco",
    }

    result = structure_company_data(json_data, "https://structured.com")

    assert result["company_name"] == "Structured Corp"
    assert result["website"] == "https://structured.com"
    assert result["description"] == "A structured company"
    assert len(result["owners"]) == 2
    assert result["owners"][0]["name"] == "John Doe"
    assert result["owners"][0]["title"] == "CEO"
    assert result["owners"][0]["ownership_percentage"] == "60%"
    assert result["owners"][1]["name"] == "Jane Smith"
    assert result["owners"][1]["title"] == "CTO"
    assert result["industry"] == "Technology"


def test_structure_company_data_string_owners():
    """Test structuring data with string owners."""
    json_data = {
        "company_name": "String Corp",
        "description": "Company with string owners",
        "owners": ["John Doe", "Jane Smith"],
    }

    result = structure_company_data(json_data, "https://string.com")

    assert len(result["owners"]) == 2
    assert result["owners"][0]["name"] == "John Doe"
    assert result["owners"][0]["title"] is None
    assert result["owners"][1]["name"] == "Jane Smith"


def test_extract_field_from_text():
    """Test extracting fields from text."""
    text = """
    Company Name: Example Corporation
    Description: We are a technology company that builds software.
    Industry: Technology
    """

    assert extract_field_from_text(text, ["company name"]) == "Example Corporation"
    assert extract_field_from_text(text, ["description"]) == "We are a technology company that builds software"
    assert extract_field_from_text(text, ["industry"]) == "Technology"
    assert extract_field_from_text(text, ["nonexistent"]) is None


def test_extract_owners_from_text():
    """Test extracting owners from text."""
    text = """
    The company was founded by John Doe and Jane Smith.
    CEO: Robert Johnson
    Founders: Alice Cooper, Bob Dylan
    Owner: Charlie Brown
    """

    owners = extract_owners_from_text(text)

    # Should find multiple owners from different patterns
    assert len(owners) > 0
    owner_names = [owner["name"] for owner in owners]

    # Check that some expected names are found
    found_names = []
    for name in owner_names:
        if any(
            expected in name
            for expected in ["John Doe", "Jane Smith", "Robert Johnson", "Alice Cooper", "Bob Dylan", "Charlie Brown"]
        ):
            found_names.append(name)

    assert len(found_names) > 0


def test_parse_text_response():
    """Test parsing a text response."""
    text = """
    Company Name: Text Corp
    Description: A company that processes text
    Industry: Technology
    Founded: 2021
    Headquarters: New York
    Founder: John Text
    """

    result = parse_text_response(text, "https://text.com")

    assert result["company_name"] == "Text Corp"
    assert result["website"] == "https://text.com"
    assert result["description"] == "A company that processes text"
    assert result["industry"] == "Technology"
    assert result["founded_year"] == "2021"
    assert result["headquarters"] == "New York"
    assert len(result["owners"]) > 0


def test_parse_company_info_with_json():
    """Test parsing company info with JSON response."""
    content = """
    ```json
    {
        "company_name": "JSON Corp",
        "description": "A JSON-based company",
        "owners": [{"name": "JSON Owner", "title": "CEO"}]
    }
    ```
    """

    result = parse_company_info(content, "https://json.com")

    assert result["company_name"] == "JSON Corp"
    assert result["description"] == "A JSON-based company"
    assert len(result["owners"]) == 1
    assert result["owners"][0]["name"] == "JSON Owner"


def test_parse_company_info_with_text():
    """Test parsing company info with text response."""
    content = """
    Company Name: Text Corp
    Description: A text-based company
    Founder: Text Owner
    """

    result = parse_company_info(content, "https://text.com")

    assert result["company_name"] == "Text Corp"
    assert result["description"] == "A text-based company"


def test_parse_company_info_error_handling():
    """Test error handling in parsing."""
    content = None  # This should cause an error

    result = parse_company_info(content, "https://error.com")

    assert result["company_name"] == "Unknown"
    assert result["website"] == "https://error.com"
    assert "Error parsing response" in result["description"]


def test_clean_response_content():
    """Test cleaning response content."""
    content = """
    
    This   is    a   messy
    
    response   with   lots
    
    of    whitespace.
    
    """

    cleaned = clean_response_content(content)

    assert cleaned == "This is a messy response with lots of whitespace."
    assert "\n" not in cleaned
    assert "  " not in cleaned  # No double spaces
