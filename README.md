# Company Owners Finder

Find company owners, founders, and detailed company information using the Perplexity AI API.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Perplexity API key:
   ```bash
   export PERPLEXITY_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```bash
   # Single company
   python main.py https://example.com
   
   # Batch processing
   python main.py urls.txt
   ```

## Usage

### Single Company
```bash
python main.py https://example.com
python main.py --url https://example.com
python main.py --api-key your_key https://example.com
```

### Batch Processing
Create a text file with URLs (one per line):
```
https://www.company1.com/
https://www.company2.com/
```

Then run:
```bash
python main.py urls.txt
python main.py --file urls.txt
```

### Help
```bash
python main.py --help
```

## Example Output

```
Company Information:
Name: OpenAI
Owners/Founders:
  • Sam Altman - Co-founder
  • Elon Musk - Co-founder
Description: OpenAI is an artificial intelligence research organization...
Industry: Artificial Intelligence
Headquarters: San Francisco, California, United States
CEO: Sam Altman - Chief Executive Officer
```

## Features

- Finds actual company owners and founders
- Dual search strategy for better results
- Batch processing for multiple companies

## API Key

Set via environment variable (recommended):
```bash
export PERPLEXITY_API_KEY=your_key
```

Or via command line:
```bash
python main.py --api-key your_key https://example.com
```
