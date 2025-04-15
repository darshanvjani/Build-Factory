import os
import json
import asyncio
from pdf_splitter import split_pdf
from parallel_processor import run_parallel_processing
from contextual_text import process_pdf_pages_parallel

# Hardcoded configuration
INPUT_PDF = r"output_pdfs\main.pdf"
OUTPUT_DIR = "output"
UNSTRUCTURED_API_KEY = "Dk2o22hmDS9lBoFxH3YLNwU8jLXLtf"  # Replace with your actual API key
OPENAI_API_KEY = "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"
SKIP_FIRST_PAGE = True

async def process_pdf(input_pdf, output_dir, unstructured_api_key, openai_api_key, skip_first_page=True):
    """
    Process a PDF file in parallel.
    
    Args:
        input_pdf (str): Path to the input PDF file
        output_dir (str): Directory to save output files
        unstructured_api_key (str): Unstructured Cloud API key
        openai_api_key (str): OpenAI API key
        skip_first_page (bool): Whether to skip the first page (default: True)
        
    Returns:
        dict: Combined structured data for all pages
    """
    # Create output directories
    split_pdf_dir = os.path.join(output_dir, 'split_pdf')
    image_dir = os.path.join(output_dir, 'page_imgs')
    os.makedirs(split_pdf_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    
    # Step 1: Split the PDF into individual pages
    print(f"✅ Splitting PDF: {input_pdf}")
    pdf_files = split_pdf(input_pdf, split_pdf_dir, skip_first_page)
    print(f"✅ Split PDF into {len(pdf_files)} pages")
    
    # Step 2: Process pages in parallel
    print("✅ Processing pages in parallel...")
    combined_results = await run_parallel_processing(
        pdf_files=pdf_files,
        output_image_dir=image_dir,
        unstructured_api_key=unstructured_api_key,
        openai_api_key=openai_api_key
    )
    
    return combined_results

async def main():
    # Process the PDF using hardcoded values
    combined_results = await process_pdf(
        input_pdf=INPUT_PDF,
        output_dir=OUTPUT_DIR,
        unstructured_api_key=UNSTRUCTURED_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        skip_first_page=SKIP_FIRST_PAGE
    )
    
    # Save the combined results
    output_json_path = os.path.join(OUTPUT_DIR, 'combined_results.json')
    with open(output_json_path, 'w') as f:
        json.dump(combined_results, f, indent=2)
    
    print(f"✅ Combined results saved to {output_json_path}")
    print("✅ Processing complete!")

if __name__ == "__main__":
    asyncio.run(main())
