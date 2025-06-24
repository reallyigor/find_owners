import json


def save_to_json(data, filename=None):
    """
    Save company data to a JSON file.

    Args:
        data (dict): Company information to save
        filename (str, optional): Output filename. If not provided, uses company name.

    Returns:
        str: The filename that was used
    """
    if not filename:
        company_name = data.get("company_name") or "unknown_company"
        # Clean company name for filename
        clean_name = "".join(c for c in str(company_name) if c.isalnum() or c in (" ", "-", "_")).rstrip()
        clean_name = clean_name.replace(" ", "_").lower()
        if not clean_name:  # If name becomes empty after cleaning
            clean_name = "unknown_company"
        filename = f"results/{clean_name}_info.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filename
