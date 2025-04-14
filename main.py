import os
import json
import openai
from pdf2image import convert_from_path
from contextual_text import get_clean_contextual_text_from_page
from openai_module import extract_structured_data_from_plumbing_drawing

# Configuration
pdf_path = r"output_pdfs\page_2.pdf"
poppler_path = r"C:\Users\Janid\OneDrive\Temp\Release-24.08.0-0\poppler-24.08.0\Library\bin"
output_image_path = r"output_pdfs\page_2.png"
page_number = 2

# Set your OpenAI API key
openai.api_key = "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"

# Step 1: Extract and clean contextual text
elements, context_text = get_clean_contextual_text_from_page(pdf_path, poppler_path)
print("✅ Extracted and cleaned contextual text.")

# Step 2: Convert PDF page to high-resolution PNG
images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
if images:
    images[0].save(output_image_path, "PNG")
    print(f"✅ Saved high-resolution page image to {output_image_path}")
else:
    raise Exception("No images generated from PDF.")

# Step 3: Extract structured data using the multimodal LLM
structured_output = extract_structured_data_from_plumbing_drawing(
    image_path=output_image_path,
    context_text=context_text,
    page_number=page_number,
    api_key=openai.api_key
)

print("✅ Structured Output from Multimodal LLM:")
print(structured_output)

# Save the structured output to a JSON file
with open("structured_output_page_2.json", "w") as f:
    json.dump({"page": page_number, "structured_output": structured_output}, f, indent=2)
