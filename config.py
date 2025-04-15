"""
Configuration settings for the PDF processing system.
"""

# File paths
INPUT_PDF = r"output_pdfs\main.pdf"
OUTPUT_DIR = "output"

# API Keys
UNSTRUCTURED_API_KEY = ""
OPENAI_API_KEY = ""

# Processing settings
SKIP_FIRST_PAGE = True
TIMEOUT_SECONDS = 600  # 10 minutes timeout for API requests
MAX_RETRIES = 3  # Number of retries for failed requests

# API endpoints
UNSTRUCTURED_API_URL = "https://api.unstructuredapp.io/general/v0/general"

# OpenAI settings
OPENAI_MODEL = "gpt-4.1-2025-04-14"  # Default model for OpenAI API calls

# File size thresholds (in MB)
LARGE_FILE_THRESHOLD = 5  # Files larger than this will get a warning 