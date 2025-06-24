"""
Company Owners Finder Package

A modular Python application that uses the Perplexity AI API to find company owners and descriptions.
"""

__version__ = "1.0.0"
__author__ = "Company Owners Finder"

from .parser import find_company_owners
from .models import create_company_info, create_owner, create_management_info, create_executive_info
from .utils import save_to_json

__all__ = ["find_company_owners", "create_company_info", "create_owner", "create_management_info", "create_executive_info", "save_to_json"]
