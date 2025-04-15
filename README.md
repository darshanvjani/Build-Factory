# PDF Processing System

This system processes PDF files containing plumbing drawings, extracts structured data from each page, and combines the results into a single JSON output.

## Features

- Splits a PDF into individual pages (skipping the first page by default)
- Extracts contextual text from each page using Unstructured Cloud API
- Converts pages to high-resolution PNG images
- Processes pages in parallel using GPT-4 Vision
- Combines all results into a single JSON output

## Requirements

- Python 3.8+
- Unstructured Cloud API key
- OpenAI API key

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your API keys:
   - Get an Unstructured Cloud API key from [unstructured.io](https://unstructured.io)
   - Get an OpenAI API key from [OpenAI](https://platform.openai.com)

## Usage

Run the script with the following command:

```
python main.py --input_pdf path/to/your/file.pdf --unstructured_api_key your_unstructured_api_key --openai_api_key your_openai_api_key
```

### Command Line Arguments

- `--input_pdf`: Path to the input PDF file (required)
- `--output_dir`: Directory to save output files (default: 'output')
- `--unstructured_api_key`: Unstructured Cloud API key (required)
- `--openai_api_key`: OpenAI API key (required)
- `--skip_first_page`: Skip the first page (default: True)

## Output

The system generates the following outputs:

1. Individual PDF pages in the `output/split_pdf` directory
2. PNG images in the `output/page_imgs` directory
3. Combined JSON results in `output/combined_results.json`

## JSON Output Format

The combined JSON output has the following structure:

```json
{
  "page 2": { ... },
  "page 3": { ... },
  ...
  "page N": { ... }
}
```

Each page entry contains the structured data extracted by GPT-4 Vision.

## License

MIT 