"""
Configuration management for the Company Owners Finder application.
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variable to store API key from command line
_command_line_api_key = None


def set_api_key_from_command_line(api_key):
    """Set the API key from command line argument."""
    global _command_line_api_key
    _command_line_api_key = api_key


def get_perplexity_api_key():
    """Get the Perplexity API key from command line argument or environment variables."""
    # First check if API key was provided via command line
    if _command_line_api_key:
        return _command_line_api_key
    
    # Fall back to environment variable
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable is required. You can also provide it via --api-key argument.")
    return api_key


def get_api_base_url():
    """Get the API base URL."""
    return os.getenv("PERPLEXITY_API_BASE_URL", "https://api.perplexity.ai")


def get_request_timeout():
    """Get the request timeout in seconds."""
    return int(os.getenv("REQUEST_TIMEOUT", "30"))


def get_api_headers():
    """Get headers for API requests."""
    return {"Authorization": f"Bearer {get_perplexity_api_key()}", "Content-Type": "application/json"}
