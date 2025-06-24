"""
Data structures for the Company Owners Finder application.
"""


def create_owner(name, title=None, ownership_percentage=None):
    """Create an owner dictionary."""
    return {"name": name, "title": title, "ownership_percentage": ownership_percentage}


def create_management_info(ceo=None, cfo=None, coo=None):
    """Create a management information dictionary."""
    management = {}
    
    if ceo:
        management["ceo"] = ceo
    if cfo:
        management["cfo"] = cfo
    if coo:
        management["coo"] = coo
        
    return management if management else None


def create_executive_info(name, title=None):
    """Create an executive information dictionary."""
    return {
        "name": name,
        "title": title
    }


def create_company_info(
    company_name, website, description, owners=None, industry=None, founded_year=None, headquarters=None, management=None
):
    """Create a company info dictionary."""
    return {
        "company_name": company_name,
        "website": website,
        "description": description,
        "owners": owners or [],
        "management": management,  # Management information (CEO, CFO, COO)
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
        "management": {
            "ceo": {
                "name": "John Doe",
                "title": "Chief Executive Officer"
            },
            "cfo": {
                "name": "Jane Smith",
                "title": "Chief Financial Officer"
            },
            "coo": {
                "name": "Bob Johnson",
                "title": "Chief Operating Officer"
            }
        },
        "industry": "Technology",
        "founded_year": "2020",
        "headquarters": "San Francisco, CA"
    }
