import os
import json
import asyncio
from pdf2image import convert_from_path
from contextual_text import get_clean_contextual_text_from_page, process_pdf_pages_parallel
from openai_module import extract_structured_data_from_plumbing_drawing
from typing import List, Dict, Any

class ParallelProcessor:
    def __init__(self, output_image_dir, unstructured_api_key, openai_api_key):
        """
        Initialize the parallel processor.
        
        Args:
            output_image_dir (str): Directory to save PNG images
            unstructured_api_key (str): Unstructured Cloud API key
            openai_api_key (str): OpenAI API key
        """
        self.output_image_dir = output_image_dir
        self.unstructured_api_key = unstructured_api_key
        self.openai_api_key = openai_api_key
        
        # Create output directory if it doesn't exist
        os.makedirs(output_image_dir, exist_ok=True)
    
    async def process_page(self, pdf_path, page_number):
        """
        Process a single page: extract text, convert to image, and get GPT response.
        
        Args:
            pdf_path (str): Path to the PDF page
            page_number (int): Page number
            
        Returns:
            dict: Structured data for the page
        """
        # Extract contextual text using Unstructured Cloud API
        elements, context_text = await get_clean_contextual_text_from_page(pdf_path, self.unstructured_api_key)
        
        # Convert PDF to PNG
        output_image_path = os.path.join(self.output_image_dir, f"page_{page_number}.png")
        images = convert_from_path(pdf_path, dpi=300)
        if images:
            images[0].save(output_image_path, "PNG")
        else:
            raise Exception(f"No images generated from PDF: {pdf_path}")
        
        # Get GPT response
        structured_output = extract_structured_data_from_plumbing_drawing(
            image_path=output_image_path,
            context_text=context_text,
            page_number=page_number,
            api_key=self.openai_api_key
        )
        
        # Parse the JSON response
        try:
            return json.loads(structured_output)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON response for page {page_number}")
            return {"error": "Invalid JSON response", "raw_response": structured_output}
    
    async def process_pages_parallel(self, pdf_files):
        """
        Process multiple PDF pages in parallel.
        
        Args:
            pdf_files (list): List of PDF file paths
            
        Returns:
            dict: Combined structured data for all pages
        """
        # Create tasks for each page
        tasks = []
        for pdf_file in pdf_files:
            # Extract page number from filename (assuming format: page_X.pdf)
            page_number = int(os.path.basename(pdf_file).split('_')[1].split('.')[0])
            tasks.append(self.process_page(pdf_file, page_number))
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Combine results into a single JSON object
        combined_results = {}
        for i, result in enumerate(results):
            page_number = int(os.path.basename(pdf_files[i]).split('_')[1].split('.')[0])
            combined_results[f"page {page_number}"] = result
        
        return combined_results

async def run_parallel_processing(
    pdf_files: List[str],
    output_image_dir: str,
    unstructured_api_key: str,
    openai_api_key: str,
    max_workers: int = None
) -> Dict[str, Any]:
    """
    Run parallel processing of PDF files.
    
    Args:
        pdf_files (List[str]): List of PDF file paths
        output_image_dir (str): Directory to save output images
        unstructured_api_key (str): Unstructured Cloud API key
        openai_api_key (str): OpenAI API key
        max_workers (int, optional): Maximum number of worker threads
        
    Returns:
        Dict[str, Any]: Combined results from all pages
    """
    print(f"Starting parallel processing with {len(pdf_files)} files")
    processor = ParallelProcessor(output_image_dir, unstructured_api_key, openai_api_key)
    
    # Process all pages in parallel
    tasks = []
    for pdf_file in pdf_files:
        page_number = int(os.path.basename(pdf_file).split('_')[1].split('.')[0])
        tasks.append(processor.process_page(pdf_file, page_number))
    
    print(f"Processing all {len(pdf_files)} pages in parallel...")
    try:
        # Process all pages at once
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        results = {}
        for i, result in enumerate(batch_results):
            page_number = int(os.path.basename(pdf_files[i]).split('_')[1].split('.')[0])
            if isinstance(result, Exception):
                print(f"Error processing page {page_number}: {str(result)}")
                results[str(page_number)] = {"error": str(result)}
            else:
                results[str(page_number)] = result
                print(f"Completed processing page {page_number}")
                
    except Exception as e:
        import traceback
        print(f"Error during processing: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
    
    return results 