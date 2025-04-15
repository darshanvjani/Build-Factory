# PDF Processing System for Plumbing Drawings

This system processes PDF files containing plumbing drawings, extracts structured data from each page using AI, and combines the results into a single JSON output. It uses a combination of Unstructured Cloud API for text extraction and OpenAI's GPT-4 Vision for intelligent analysis.

## System Architecture

The system consists of several components working together:

1. **PDF Processing Pipeline**:
   - Splits input PDF into individual pages
   - Processes pages in parallel for efficiency
   - Uses 10-minute timeout for API requests to handle large files
   - Implements retry mechanism with exponential backoff

2. **Text Extraction (Unstructured Cloud API)**:
   - Extracts contextual text from PDF pages
   - Maintains layout awareness
   - Sorts text elements logically (top-to-bottom, left-to-right)
   - Cleans up vertical/garbled characters

3. **Image Processing**:
   - Converts PDF pages to high-resolution PNG images
   - Uses 300 DPI for optimal quality
   - Saves images for visual analysis

4. **AI Analysis (OpenAI GPT-4 Vision)**:
   - Analyzes both extracted text and images
   - Identifies plumbing components
   - Extracts specifications and dimensions
   - Provides confidence scores for each item

## Features

- Parallel processing of PDF pages
- Intelligent text extraction with layout preservation
- High-resolution image conversion
- AI-powered plumbing component identification
- Confidence scoring for extracted items
- Detailed error handling and retries
- Configurable settings via `config.py`

## Prerequisites

- Python 3.8+
- Unstructured Cloud API key
- OpenAI API key
- Poppler (for PDF to image conversion)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Poppler (required for PDF to image conversion):
   - Windows: Download from [poppler releases](http://blog.alivate.com.au/poppler-windows/)
   - Linux: `sudo apt-get install poppler-utils`
   - Mac: `brew install poppler`

4. Configure API keys in `config.py`:
   ```python
   UNSTRUCTURED_API_KEY = "your-unstructured-api-key"
   OPENAI_API_KEY = "your-openai-api-key"
   ```

## Configuration

The system is configured through `config.py`. Key settings include:

```python
# File paths
INPUT_PDF = "path/to/your/input.pdf"
OUTPUT_DIR = "output"

# API settings
TIMEOUT_SECONDS = 600  # 10 minutes timeout
MAX_RETRIES = 3       # Number of retry attempts

# Processing settings
SKIP_FIRST_PAGE = True
LARGE_FILE_THRESHOLD = 5  # MB
```

## Usage

1. Place your PDF file in the specified input directory (default: `output_pdfs/main.pdf`)

2. Run the main script:
   ```bash
   python main.py
   ```

3. The system will:
   - Split the PDF into pages
   - Process each page in parallel
   - Generate PNG images
   - Extract and analyze text
   - Save results to `output/combined_results.json`

## Output Format

The system generates a JSON file with the following structure:

```json
{
  "page 2": {
    "page": 2,
    "plumbing_items": [
      {
        "item_type": "pipe",
        "quantity": 1,
        "model_or_spec": "HHWR",
        "dimensions": "2\" Ø",
        "mounting_type": "ceiling-mounted",
        "confidence": 0.95,
        "notes": "N/A"
      }
    ]
  }
}
```

## Error Handling

The system includes robust error handling:
- Automatic retries for failed API requests
- Exponential backoff between retries
- Detailed error logging
- File size warnings for large PDFs
- Graceful handling of API timeouts

## Performance Considerations

- Large files (>5MB) may take longer to process
- System processes all pages in parallel for optimal speed
- 10-minute timeout per request ensures completion of large files
- Batch processing with configurable retry attempts

## Troubleshooting

1. **API Timeouts**:
   - Check your internet connection
   - Verify API keys are correct
   - Consider increasing `TIMEOUT_SECONDS` in config.py

2. **PDF Processing Issues**:
   - Ensure Poppler is properly installed
   - Verify PDF file is not corrupted
   - Check file permissions

3. **Memory Issues**:
   - Reduce batch size for very large PDFs
   - Monitor system resources during processing

## License

MIT License 