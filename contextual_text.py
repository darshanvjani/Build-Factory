import re
import html
import json
import os
import asyncio
import aiohttp
from typing import List, Tuple, Dict, Any
import backoff  # We'll need to install this

async def get_clean_contextual_text_from_page(pdf_path: str, api_key: str) -> tuple:
    """
    High-level function to extract and clean context-aware text from a single-page PDF using Unstructured Cloud.
    This includes:
    - Layout-aware partitioning using Unstructured Cloud API
    - Logical sorting (top-to-bottom, left-to-right)
    - Cleanup of vertical/garbled characters and HTML/unicode
    
    Args:
        pdf_path (str): Path to the PDF file
        api_key (str): Unstructured Cloud API key
        
    Returns:
        tuple: (elements, cleaned_text) where elements are the raw extracted elements
               and cleaned_text is the processed and cleaned text
    """
    print(f"Processing file: {pdf_path}")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # API endpoint
    url = "https://api.unstructuredapp.io/general/v0/general"
    headers = {
        "accept": "application/json",
        "unstructured-api-key": api_key
    }

    # Get file size to check if it's too large
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # Size in MB
    print(f"File size: {file_size:.2f} MB")
    
    # If file is too large, we might need to adjust our approach
    if file_size > 10:  # If file is larger than 10MB
        print(f"Warning: File is large ({file_size:.2f} MB). This might cause timeout issues.")

    # Use a longer timeout for larger files
    timeout = aiohttp.ClientTimeout(total=600)  # 10 minutes total timeout
    
    # Try up to 3 times with exponential backoff
    for attempt in range(3):
        try:
            # Process the PDF using the cloud API
            print(f"Sending request to API for {pdf_path} (attempt {attempt+1}/3)")
            
            # Use aiohttp for asynchronous HTTP requests
            async with aiohttp.ClientSession(timeout=timeout) as session:
                with open(pdf_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('files', f, filename=os.path.basename(pdf_path), content_type='application/pdf')
                    
                    params = {
                        'strategy': 'hi_res',
                        'coordinates': 'true',
                        'infer_table_structure': 'true'
                    }
                    
                    try:
                        async with session.post(url, headers=headers, data=data, params=params) as response:
                            print(f"Received response for {pdf_path}")
                            response.raise_for_status()
                            elements = await response.json()
                            # If we get here, the request was successful
                            break
                    except aiohttp.ClientResponseError as e:
                        error_text = await response.text()
                        print(f"API Error Response: {error_text}")
                        if attempt < 2:  # If not the last attempt
                            wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                            print(f"Retrying in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            continue
                        raise Exception(f"API Error: {e.status} - {e.message}. Response: {error_text}")
        except asyncio.TimeoutError:
            if attempt < 2:  # If not the last attempt
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"Request timed out. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                continue
            raise Exception(f"Request timed out after {timeout.total} seconds")
        except aiohttp.ClientError as e:
            if attempt < 2:  # If not the last attempt
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"Connection error: {str(e)}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                continue
            raise Exception(f"Connection error: {str(e)}. Please check your internet connection and API endpoint.")
        except Exception as e:
            if attempt < 2:  # If not the last attempt
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"Error: {str(e)}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                continue
            import traceback
            print(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Error partitioning PDF: {str(e)}")
    
    # Step 2: Sort elements by Y then X coordinates
    def get_coords(el):
        coords = el.get('metadata', {}).get('coordinates', {})
        if coords and coords.get('points'):
            x, y = coords['points'][0]
            return (round(y, 2), round(x, 2))
        return (9999, 9999)

    sorted_elements = sorted(
        [el for el in elements if el.get('text') and el.get('metadata', {}).get('coordinates', {}).get('points')],
        key=get_coords
    )

    raw_merged = "\n".join(el['text'].strip() for el in sorted_elements)

    def clean_text(text: str) -> str:
        text = text.encode('utf-8').decode('unicode_escape')
        text = html.unescape(text)

        lines = text.split('\n')
        cleaned_lines = []
        buffer = []

        for line in lines:
            stripped = line.strip()
            if len(stripped) <= 2 and not re.match(r'\w{2,}', stripped):
                buffer.append(stripped)
            else:
                if len(buffer) >= 5:
                    buffer = []  # drop junk
                else:
                    cleaned_lines.extend(buffer)
                    buffer = []
                cleaned_lines.append(stripped)
        if buffer and len(buffer) < 5:
            cleaned_lines.extend(buffer)

        text = "\n".join(cleaned_lines)
        text = re.sub(r'\n{2,}', '\n', text)
        text = re.sub(r'[ ]{2,}', ' ', text)
        return text.strip()

    cleaned_text = clean_text(raw_merged)
    return (elements, cleaned_text)


async def process_pdf_pages_parallel(
    pdf_files: List[str], 
    api_key: str,
    max_workers: int = None
) -> Dict[int, Tuple[Any, str]]:
    """
    Process multiple PDF pages in parallel using the Unstructured Cloud API.
    
    Args:
        pdf_files (List[str]): List of PDF file paths to process
        api_key (str): Unstructured Cloud API key
        max_workers (int, optional): Maximum number of worker threads. Defaults to None (CPU count)
        
    Returns:
        Dict[int, Tuple[Any, str]]: Dictionary mapping page numbers to their processed results
    """
    # Create tasks for all pages
    tasks = []
    for pdf_file in pdf_files:
        # Extract page number from filename (assuming format: page_X.pdf)
        page_number = int(os.path.basename(pdf_file).split('_')[1].split('.')[0])
        tasks.append(get_clean_contextual_text_from_page(pdf_file, api_key))
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Convert results to dictionary
    return {
        int(os.path.basename(pdf_files[i]).split('_')[1].split('.')[0]): result 
        for i, result in enumerate(results)
    }


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract and clean contextual text from PDF pages in parallel.')
    parser.add_argument('--pdf_dir', required=True, help='Directory containing PDF files')
    parser.add_argument('--api_key', required=True, help='Unstructured Cloud API key')
    parser.add_argument('--output_dir', default='output', help='Directory to save output files')
    parser.add_argument('--max_workers', type=int, help='Maximum number of worker threads')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get all PDF files in the directory
    pdf_files = [
        os.path.join(args.pdf_dir, f) for f in os.listdir(args.pdf_dir)
        if f.endswith('.pdf') and f.startswith('page_')
    ]
    
    # Process all pages in parallel
    async def main():
        results = await process_pdf_pages_parallel(
            pdf_files=pdf_files,
            api_key=args.api_key,
            max_workers=args.max_workers
        )
        
        # Save results
        for page_number, (elements, context_text) in results.items():
            output_file = os.path.join(args.output_dir, f"cleaned_contextual_text_page_{page_number}.json")
            with open(output_file, "w") as f:
                json.dump({
                    "page": page_number,
                    "contextual_text": context_text
                }, f, indent=2)
            print(f"✅ Processed page {page_number} -> {output_file}")
    
    # Run the async main function
    asyncio.run(main())
