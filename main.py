import json
import sys
import os
import argparse

from owners_finder import find_company_owners, save_to_json
from owners_finder.config import set_api_key_from_command_line


def process_single_url(website_url):
    """Process a single website URL and display results."""
    try:
        print(f"Analyzing company website: {website_url}")

        # Find company owners
        company_info = find_company_owners(website_url)

        # Save to JSON file
        filename = save_to_json(company_info)

        # Print results
        print(f"\nCompany Information:")
        print(f"Name: {company_info['company_name']}")
        
        # Display Owners/Founders as second row
        if company_info.get("owners") and len(company_info["owners"]) > 0:
            print(f"Owners/Founders:")
            for owner in company_info["owners"]:
                owner_info = owner.get("name") or "Unknown"
                if owner.get("title"):
                    owner_info += f" - {owner['title']}"
                if owner.get("ownership_percentage"):
                    owner_info += f" ({owner['ownership_percentage']})"
                print(f"  • {owner_info}")
        else:
            print("Owners/Founders: Not found")
        
        print(f"Description: {company_info['description']}")
        print(f"Industry: {company_info.get('industry', 'Not specified')}")
        print(f"Headquarters: {company_info.get('headquarters', 'Not specified')}")
        
        # Display CEO information
        if company_info.get('ceo'):
            ceo = company_info['ceo']
            ceo_info = ceo.get('name') or "Unknown"
            if ceo.get('title'):
                ceo_info += f" - {ceo['title']}"
            print(f"CEO: {ceo_info}")
        else:
            print("CEO: Not found")

        print(f"\nResults saved to: {filename}")

        # Also print JSON for easy copying
        print(f"\nJSON Output:")
        print(json.dumps(company_info, indent=2))

        return True

    except ValueError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Failed to analyze company: {e}")
        return False


def process_urls_from_file(file_path):
    """Process multiple URLs from a text file."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return False

        # Read URLs from file
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]

        if not urls:
            print(f"Error: No URLs found in file '{file_path}'.")
            return False

        print(f"Found {len(urls)} URLs to process from '{file_path}'")
        print("=" * 60)

        # Process each URL
        successful = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            print("-" * 40)
            
            if process_single_url(url):
                successful += 1
            else:
                failed += 1
            
            print("-" * 40)

        # Summary
        print(f"\n" + "=" * 60)
        print(f"BATCH PROCESSING COMPLETE")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total: {len(urls)}")
        print("=" * 60)

        return successful > 0

    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return False


def validate_url(url):
    """Validate if the input is a valid URL."""
    return url.startswith(('http://', 'https://'))


def validate_file(file_path):
    """Validate if the input is a valid text file."""
    if not os.path.isfile(file_path):
        return False
    return file_path.endswith('.txt')


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Company Owners Finder - Find company information and ownership details",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://example.com
  python main.py urls.txt
  python main.py --file urls.txt
  python main.py --url https://example.com
  python main.py --api-key YOUR_API_KEY https://example.com
  python main.py --api-key YOUR_API_KEY --file urls.txt
        """
    )
    
    # Add API key argument
    parser.add_argument(
        '--api-key',
        help='Perplexity API key (overrides PERPLEXITY_API_KEY environment variable)'
    )
    
    # Create a mutually exclusive group for input types
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        'input',
        nargs='?',
        help='URL or text file containing URLs to process'
    )
    input_group.add_argument(
        '--url',
        help='Single URL to process'
    )
    input_group.add_argument(
        '--file',
        help='Text file containing URLs (one per line)'
    )

    args = parser.parse_args()

    # Set API key from command line if provided
    if args.api_key:
        set_api_key_from_command_line(args.api_key)

    # Determine the input to process
    if args.url:
        input_path = args.url
    elif args.file:
        input_path = args.file
    else:
        input_path = args.input

    # Validate and process the input
    if validate_url(input_path):
        # Process single URL
        success = process_single_url(input_path)
        if not success:
            sys.exit(1)
    elif validate_file(input_path):
        # Process URLs from file
        success = process_urls_from_file(input_path)
        if not success:
            sys.exit(1)
    else:
        print("Error: Input must be either:")
        print("  - A valid URL starting with http:// or https://")
        print("  - A .txt file containing URLs (one per line)")
        sys.exit(1)


if __name__ == "__main__":
    main()
