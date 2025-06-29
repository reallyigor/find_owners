"""
Parser module for extracting company information from Perplexity API responses.
"""

import json
import re

import requests

from owners_finder.api_client import call_perplexity_api, create_company_prompt, create_owners_prompt, extract_content_from_response
from owners_finder.models import create_company_info, create_owner, validate_url, create_management_info, create_executive_info


def find_company_owners(website_url):
    """
    Find company owners and information for a given website URL.

    Args:
        website_url (str): The company website URL

    Returns:
        dict: Company information including owners

    Raises:
        ValueError: If the URL is invalid
        Exception: If the API call or parsing fails
    """
    # Validate the URL
    if not validate_url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")

    try:
        # Create the prompt for the API
        prompt = create_company_prompt(website_url)

        # Call the Perplexity API
        api_response = call_perplexity_api(prompt)

        # Check if we got a valid response
        if not api_response:
            raise Exception("Received empty response from API")

                # Extract content from the response
        content = extract_content_from_response(api_response)

        # Clean the content
        cleaned_content = clean_response_content(content)



        # Parse the company information
        company_info = parse_company_info(cleaned_content, website_url)

        # If no owners were found, make a second API call specifically for owners
        if not company_info.get("owners") or len(company_info["owners"]) == 0:
            try:
                company_name = company_info.get("company_name", "Unknown")
                if company_name and company_name != "Unknown":
                    print(f"No owners found in initial search. Searching specifically for {company_name} owners...")
                    
                    # Create owners-specific prompt
                    owners_prompt = create_owners_prompt(company_name)
                    
                    # Make second API call
                    owners_response = call_perplexity_api(owners_prompt)
                    
                    if owners_response:
                        # Extract and parse owners content
                        owners_content = extract_content_from_response(owners_response)
                        cleaned_owners_content = clean_response_content(owners_content)
                        
                        # Try to extract owners and management from the response
                        additional_owners, additional_management = parse_owners_response(cleaned_owners_content)
                        
                        if additional_owners:
                            company_info["owners"] = additional_owners
                            print(f"Found {len(additional_owners)} owner(s) in detailed search.")
                        else:
                            print("No additional owners found in detailed search.")
                        
                        # Merge management information if found
                        if additional_management:
                            if not company_info.get("management"):
                                company_info["management"] = additional_management
                            else:
                                # Merge with existing management info
                                existing_management = company_info["management"]
                                for role in ["ceo", "cfo", "coo"]:
                                    if role in additional_management and additional_management[role]:
                                        if not existing_management.get(role):
                                            existing_management[role] = additional_management[role]
                    
            except Exception as e:
                print(f"Warning: Failed to find additional owners: {str(e)}")
                # Continue with original results even if second call fails

        return company_info

    except ValueError as e:
        # Re-raise ValueError as is (these are usually API key or validation issues)
        raise e
    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to find company owners: {str(e)}")


def parse_company_info(api_content, website_url):
    """
    Parse company information from API response content.

    Args:
        api_content (str): The content from the API response
        website_url (str): The original website URL

    Returns:
        dict: Parsed company information
    """
    try:
        # Check if content is valid
        if not api_content:
            raise ValueError("API content is empty or None")

        # Try to extract JSON from the response
        json_data = extract_json_from_text(api_content)

        if json_data:
            return structure_company_data(json_data, website_url)
        else:
            # Fallback to text parsing if no JSON found
            return parse_text_response(api_content, website_url)

    except Exception as e:
        # If all parsing fails, return basic structure with error info
        return create_company_info(
            company_name="Unknown", website=website_url, description=f"Error parsing response: {str(e)}", owners=[]
        )


def extract_json_from_text(text):
    """
    Extract JSON object from text that might contain additional content.

    Args:
        text (str): Text that may contain JSON

    Returns:
        dict or None: Parsed JSON data or None if not found
    """
    # Try parsing the entire text as JSON first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in the text
    json_patterns = [
        r"```json\s*(\{.*?\})\s*```",  # JSON in code blocks
        r"```\s*(\{.*?\})\s*```",  # JSON in code blocks without language
        r"(\{.*\})",  # Any JSON-like structure - simplified pattern
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                # Clean up the match by removing any trailing text after the closing brace
                cleaned_match = match.strip()
                # Find the last closing brace to ensure we have a complete JSON
                last_brace = cleaned_match.rfind('}')
                if last_brace != -1:
                    cleaned_match = cleaned_match[:last_brace + 1]
                return json.loads(cleaned_match)
            except json.JSONDecodeError:
                continue

    return None


def structure_company_data(json_data, website_url):
    """
    Structure the parsed JSON data into our standard format.

    Args:
        json_data (dict): Parsed JSON data
        website_url (str): The original website URL

    Returns:
        dict: Structured company information
    """
    if not json_data:
        return create_company_info(
            company_name="Unknown", website=website_url, description="No data available", owners=[]
        )

    # Extract owners
    owners = []
    raw_owners = json_data.get("owners", [])

    if raw_owners and isinstance(raw_owners, list):
        for owner_data in raw_owners:
            if isinstance(owner_data, dict):
                name = owner_data.get("name") or "Unknown"
                owner = create_owner(
                    name=name,
                    title=owner_data.get("title"),
                    ownership_percentage=owner_data.get("ownership_percentage"),
                )
                # Only add owners with valid names
                if name and name != "Unknown":
                    owners.append(owner)
            elif isinstance(owner_data, str):
                # Handle case where owner is just a string
                owner = create_owner(name=owner_data)
                owners.append(owner)

    # Extract management information
    management = None
    raw_management = json_data.get("management")
    if raw_management and isinstance(raw_management, dict):
        ceo_info = None
        cfo_info = None
        coo_info = None
        
        # Extract CEO information
        raw_ceo = raw_management.get("ceo")
        if raw_ceo and isinstance(raw_ceo, dict):
            ceo_info = create_executive_info(
                name=raw_ceo.get("name"),
                title=raw_ceo.get("title")
            )
        
        # Extract CFO information
        raw_cfo = raw_management.get("cfo")
        if raw_cfo and isinstance(raw_cfo, dict):
            cfo_info = create_executive_info(
                name=raw_cfo.get("name"),
                title=raw_cfo.get("title")
            )
        
        # Extract COO information
        raw_coo = raw_management.get("coo")
        if raw_coo and isinstance(raw_coo, dict):
            coo_info = create_executive_info(
                name=raw_coo.get("name"),
                title=raw_coo.get("title")
            )
        
        management = create_management_info(ceo=ceo_info, cfo=cfo_info, coo=coo_info)

    return create_company_info(
        company_name=json_data.get("company_name", "Unknown"),
        website=website_url,
        description=json_data.get("description", "No description available"),
        owners=owners,
        management=management,
        industry=json_data.get("industry"),
        founded_year=json_data.get("founded_year"),
        headquarters=json_data.get("headquarters"),
    )


def parse_text_response(text, website_url):
    """
    Parse company information from plain text response.
    
    Args:
        text (str): Plain text response
        website_url (str): The original website URL
        
    Returns:
        dict: Parsed company information
    """
    # Simple text parsing patterns
    company_name = extract_field_from_text(text, ["company name", "name"])
    description = extract_field_from_text(text, ["description", "about", "what"])
    industry = extract_field_from_text(text, ["industry", "sector"])
    founded = extract_field_from_text(text, ["founded", "established", "year"])
    headquarters = extract_field_from_text(text, ["headquarters", "location", "based"])
    
    # Extract owners/founders
    owners = extract_owners_from_text(text)
    
    # Extract management information
    management = extract_management_from_text(text)
    
    return create_company_info(
        company_name=company_name or "Unknown",
        website=website_url,
        description=description or "No description available",
        owners=owners,
        management=management,
        industry=industry,
        founded_year=founded,
        headquarters=headquarters
    )


def extract_field_from_text(text, keywords):
    """
    Extract a field value from text based on keywords.

    Args:
        text (str): Text to search in
        keywords (list): List of keywords to look for

    Returns:
        str or None: Extracted value or None
    """
    for keyword in keywords:
        # Look for patterns like "Company Name: Example Corp"
        pattern = rf"{keyword}[:\s]+([^\n\r.]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_owners_from_text(text):
    """
    Extract owner information from text.

    Args:
        text (str): Text to search in

    Returns:
        list: List of owner dictionaries
    """
    owners = []

    # Look for common patterns
    owner_patterns = [
        r"founder[s]?[:\s]+([^\n\r.]+)",
        r"owner[s]?[:\s]+([^\n\r.]+)",
        r"CEO[:\s]+([^\n\r.]+)",
        r"founded by[:\s]+([^\n\r.]+)",
    ]

    for pattern in owner_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean up the match and create owner
            name = match.strip()
            if name and len(name) < 100:  # Sanity check
                owner = create_owner(name=name)
                owners.append(owner)

    return owners


def extract_management_from_text(text):
    """
    Extract management information from text.

    Args:
        text (str): Text to search in

    Returns:
        dict or None: Management information dictionary or None
    """
    # Look for management patterns
    management_patterns = [
        r"management[:\s]+([^\n\r.]+)",
        r"leadership[:\s]+([^\n\r.]+)",
        r"executive[:\s]+([^\n\r.]+)",
        r"board of directors[:\s]+([^\n\r.]+)",
    ]
    
    for pattern in management_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean up the match
            name = match.strip()
            if name and len(name) < 100:  # Sanity check
                return create_management_info(
                    name=name,
                    title="Management"
                )
    
    return None


def parse_owners_response(api_content):
    """
    Parse owners and management information from API response content specifically for owners search.

    Args:
        api_content (str): The content from the API response

    Returns:
        tuple: (list of owner dictionaries, management dictionary or None)
    """
    try:
        if not api_content:
            return [], None

        # Try to extract JSON from the response
        json_data = extract_json_from_text(api_content)
        
        owners = []
        management = None
        
        if json_data:
            # Extract owners
            if "owners" in json_data:
                raw_owners = json_data["owners"]
                
                if raw_owners and isinstance(raw_owners, list):
                    for owner_data in raw_owners:
                        if isinstance(owner_data, dict):
                            name = owner_data.get("name") or "Unknown"
                            # Only add owners with valid names
                            if name and name != "Unknown":
                                owner = create_owner(
                                    name=name,
                                    title=owner_data.get("title"),
                                    ownership_percentage=owner_data.get("ownership_percentage"),
                                )
                                owners.append(owner)
                        elif isinstance(owner_data, str):
                            # Handle case where owner is just a string
                            owner = create_owner(name=owner_data)
                            owners.append(owner)
            
            # Extract management
            if "management" in json_data:
                raw_management = json_data["management"]
                if raw_management and isinstance(raw_management, dict):
                    ceo_info = None
                    cfo_info = None
                    coo_info = None
                    
                    # Extract CEO
                    if "ceo" in raw_management and raw_management["ceo"]:
                        ceo_data = raw_management["ceo"]
                        if isinstance(ceo_data, dict):
                            ceo_info = create_executive_info(
                                name=ceo_data.get("name"),
                                title=ceo_data.get("title")
                            )
                        elif isinstance(ceo_data, str):
                            ceo_info = create_executive_info(name=ceo_data)
                    
                    # Extract CFO
                    if "cfo" in raw_management and raw_management["cfo"]:
                        cfo_data = raw_management["cfo"]
                        if isinstance(cfo_data, dict):
                            cfo_info = create_executive_info(
                                name=cfo_data.get("name"),
                                title=cfo_data.get("title")
                            )
                        elif isinstance(cfo_data, str):
                            cfo_info = create_executive_info(name=cfo_data)
                    
                    # Extract COO
                    if "coo" in raw_management and raw_management["coo"]:
                        coo_data = raw_management["coo"]
                        if isinstance(coo_data, dict):
                            coo_info = create_executive_info(
                                name=coo_data.get("name"),
                                title=coo_data.get("title")
                            )
                        elif isinstance(coo_data, str):
                            coo_info = create_executive_info(name=coo_data)
                    
                    management = create_management_info(ceo=ceo_info, cfo=cfo_info, coo=coo_info)
        else:
            # Fallback to text parsing if no JSON found
            owners = extract_owners_from_text(api_content)
            management = extract_management_from_text(api_content)
        
        return owners, management
            
    except Exception as e:
        # If parsing fails, try text extraction as fallback
        owners = extract_owners_from_text(api_content)
        management = extract_management_from_text(api_content)
        return owners, management


def clean_response_content(content):
    """
    Clean and prepare response content for parsing.

    Args:
        content (str): Raw response content

    Returns:
        str: Cleaned content
    """
    # Remove citation brackets that break JSON formatting
    content = re.sub(r'\[(\d+)\]', '', content)
    
    # Remove extra whitespace and normalize line endings
    content = re.sub(r"\s+", " ", content)
    content = content.strip()

    return content
