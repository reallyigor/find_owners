"""
Data structures for the Company Owners Finder application.
"""


def create_owner(name, title=None, ownership_percentage=None):
    """Create an owner dictionary."""
    return {"name": name, "title": title, "ownership_percentage": ownership_percentage}


def create_ceo_info(name, title=None):
    """Create a CEO information dictionary."""
    return {
        "name": name,
        "title": title or "CEO"
    }


def create_company_info(
    company_name, website, description, owners=None, industry=None, founded_year=None, headquarters=None, ceo=None
):
    """Create a company info dictionary."""
    return {
        "company_name": company_name,
        "website": website,
        "description": description,
        "owners": owners or [],
        "ceo": ceo,  # Dedicated CEO information
        "industry": industry,
        "founded_year": founded_year,
        "headquarters": headquarters
    }


def validate_url(url):
    """Simple URL validation."""
    if not url or not isinstance(url, str):
        return False
    return url.startswith(("http://", "https://"))


def example_company_info():
    """Return an example company info structure."""
    return {
        "company_name": "Example Corp",
        "website": "https://example.com",
        "description": "A technology company specializing in AI solutions",
        "owners": [
            {
                "name": "John Doe",
                "title": "CEO & Founder",
                "ownership_percentage": "60%"
            }
        ],
        "ceo": {
            "name": "John Doe",
            "title": "Chief Executive Officer"
        },
        "industry": "Technology",
        "founded_year": "2020",
        "headquarters": "San Francisco, CA"
    }
