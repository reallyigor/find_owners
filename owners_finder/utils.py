import json
from pathlib import Path
from datetime import datetime


def save_to_json(data, folder=Path("results"), filename=None):
    """
    Save company data to a JSON file in a date-based folder structure.

    Args:
        data (dict): Company information to save
        folder (Path): Base results folder
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
        filename = f"{clean_name}_info.json"
    else:
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'

    # Create date-based folder structure
    today = datetime.now().strftime("%Y-%m-%d")
    date_folder = folder / today
    
    if not date_folder.exists():
        date_folder.mkdir(parents=True, exist_ok=True)

    file_path = date_folder / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return file_path
