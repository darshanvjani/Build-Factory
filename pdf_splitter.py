import os
import PyPDF2

def split_pdf(input_pdf_path, output_dir, skip_first_page=True):
    """
    Split a PDF into individual pages and save them to the specified directory.
    
    Args:
        input_pdf_path (str): Path to the input PDF file
        output_dir (str): Directory to save the individual page PDFs
        skip_first_page (bool): Whether to skip the first page (default: True)
        
    Returns:
        list: List of paths to the created PDF files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the PDF file
    with open(input_pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)
        
        # Determine start page (skip first page if requested)
        start_page = 1 if skip_first_page else 0
        
        # List to store output file paths
        output_files = []
        
        # Process each page
        for page_num in range(start_page, total_pages):
            # Create a new PDF writer
            writer = PyPDF2.PdfWriter()
            
            # Add the page to the writer
            writer.add_page(reader.pages[page_num])
            
            # Generate output file path (page numbers start from 1 for user-friendliness)
            output_file = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
            
            # Write the page to a new PDF file
            with open(output_file, 'wb') as output:
                writer.write(output)
            
            output_files.append(output_file)
            
        return output_files

if __name__ == "__main__":
    # Example usage
    input_pdf = "example.pdf"
    output_dir = "split_pdf"
    output_files = split_pdf(input_pdf, output_dir)
    print(f"Split PDF into {len(output_files)} pages") 