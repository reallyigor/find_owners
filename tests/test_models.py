"""
Tests for the models module.
"""

import pytest

from owners_finder.models import create_company_info, create_owner, example_company_info, validate_url


def test_create_owner():
    """Test creating an owner dictionary."""
    # Test with all fields
    owner = create_owner("John Doe", "CEO", "60%")
    assert owner["name"] == "John Doe"
    assert owner["title"] == "CEO"
    assert owner["ownership_percentage"] == "60%"

    # Test with only name
    owner = create_owner("Jane Smith")
    assert owner["name"] == "Jane Smith"
    assert owner["title"] is None
    assert owner["ownership_percentage"] is None


def test_create_company_info():
    """Test creating a company info dictionary."""
    owners = [create_owner("John Doe", "CEO")]

    company = create_company_info(
        company_name="Test Corp",
        website="https://test.com",
        description="A test company",
        owners=owners,
        industry="Technology",
        founded_year="2020",
        headquarters="San Francisco",
    )

    assert company["company_name"] == "Test Corp"
    assert company["website"] == "https://test.com"
    assert company["description"] == "A test company"
    assert len(company["owners"]) == 1
    assert company["owners"][0]["name"] == "John Doe"
    assert company["industry"] == "Technology"
    assert company["founded_year"] == "2020"
    assert company["headquarters"] == "San Francisco"


def test_create_company_info_minimal():
    """Test creating company info with minimal data."""
    company = create_company_info(
        company_name="Minimal Corp", website="https://minimal.com", description="Minimal description"
    )

    assert company["company_name"] == "Minimal Corp"
    assert company["website"] == "https://minimal.com"
    assert company["description"] == "Minimal description"
    assert company["owners"] == []
    assert company["industry"] is None
    assert company["founded_year"] is None
    assert company["headquarters"] is None


def test_validate_url():
    """Test URL validation."""
    # Valid URLs
    assert validate_url("https://example.com") is True
    assert validate_url("http://example.com") is True
    assert validate_url("https://subdomain.example.com/path") is True

    # Invalid URLs
    assert validate_url("not-a-url") is False
    assert validate_url("ftp://example.com") is False
    assert validate_url("") is False
    assert validate_url(None) is False
    assert validate_url(123) is False


def test_example_company_info():
    """Test the example company info function."""
    example = example_company_info()

    assert "company_name" in example
    assert "website" in example
    assert "description" in example
    assert "owners" in example
    assert "industry" in example
    assert "founded_year" in example
    assert "headquarters" in example

    assert isinstance(example["owners"], list)
    assert len(example["owners"]) > 0
    assert "name" in example["owners"][0]
