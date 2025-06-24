"""
Perplexity AI API client for the Company Owners Finder application.
"""

import json

import requests

from owners_finder.config import get_api_base_url, get_api_headers, get_request_timeout


def call_perplexity_api(prompt, model="sonar-pro"):
    """
    Call the Perplexity AI API with a given prompt.

    Args:
        prompt (str): The prompt to send to the API
        model (str): The model to use for the request

    Returns:
        dict: The API response

    Raises:
        requests.RequestException: If the API call fails
        ValueError: If the response is invalid
    """
    url = f"{get_api_base_url()}/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant that provides accurate information about companies. Always provide information in a structured format.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1000,
        "temperature": 0.2,
        "top_p": 0.9,
        "stream": False,
    }

    try:
        response = requests.post(url, headers=get_api_headers(), json=payload, timeout=get_request_timeout())
        response.raise_for_status()

        response_data = response.json()

        # Debug: Check if we got a valid response
        if not response_data:
            raise ValueError("Empty response from API")

        return response_data

    except requests.RequestException as e:
        raise requests.RequestException(f"API call failed: {str(e)}")
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")


def create_company_prompt(website_url):
    """
    Create a prompt for finding company owners and information.

    Args:
        website_url (str): The company website URL

    Returns:
        str: The formatted prompt
    """
    return f"""
Please analyze the company website at {website_url}, then find and provide the following information in JSON format:

1. Company name
2. Brief description of what the company does (1-2 sentences)
3. List of owners/founders with their names and titles
4. CEO information (name and title)
5. Industry/sector
6. Year founded (if available)
7. Headquarters location (if available)

Please format the response as a JSON object with these exact keys:
- company_name
- description
- owners (array of objects with name, title, ownership_percentage)
- ceo (object with name, title)
- industry
- founded_year
- headquarters

For the CEO section, please include:
- name: Full name of the CEO
- title: Official title (CEO, Chief Executive Officer, etc.)

If any information is not available, use null for that field. Focus on publicly available information about ownership, leadership, and company details.
"""


def create_owners_prompt(company_name):
    """
    Create a prompt specifically for finding company owners/founders.

    Args:
        company_name (str): The company name

    Returns:
        str: The formatted prompt
    """
    return f"""
Find the owner of {company_name}.

Please provide the response in JSON format with these exact keys:
- owners (array of objects with name, title, ownership_percentage if known)

Each owner object should include:
- name: Full name of the owner/founder
- title: Their role/title (Founder, Owner, Major Shareholder, etc.)
- ownership_percentage: Their ownership stake if publicly known (or null if unknown)

If you cannot find specific ownership information, please indicate that in the response. Focus only on actual ownership, not just management positions.
"""


def extract_content_from_response(api_response):
    """
    Extract the main content from the Perplexity API response.

    Args:
        api_response (dict): The raw API response

    Returns:
        str: The extracted content

    Raises:
        ValueError: If the response format is unexpected
    """
    try:
        if not api_response:
            raise ValueError("API response is None or empty")

        if "choices" not in api_response or not api_response["choices"]:
            raise ValueError("No choices found in API response")

        first_choice = api_response["choices"][0]

        if "message" not in first_choice or "content" not in first_choice["message"]:
            raise ValueError("No content found in API response")

        content = first_choice["message"]["content"]
        if not content:
            raise ValueError("Content is empty in API response")

        return content

    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Unexpected response format: {str(e)}")
