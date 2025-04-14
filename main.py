import os
import json
import openai
from pdf2image import convert_from_path

from contextual_text import get_clean_contextual_text_from_page

pdf_path = r"output_pdfs\page_2.pdf"
poppler_path = r"C:\Users\Janid\OneDrive\Temp\Release-24.08.0-0\poppler-24.08.0\Library\bin"
output_image_path = r"output_pdfs\page_2.png"
page_number = 2

openai.api_key = "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"

# ----- STEP 1: Get Clean Contextual Text -----
elements, context_text = get_clean_contextual_text_from_page(pdf_path, poppler_path)
print("✅ Extracted and cleaned contextual text.")

# ----- STEP 2: Convert PDF Page to High-Resolution PNG -----
# Here we assume that the pdf_path is a one-page PDF; if multi-page, you might want to select a specific page.
images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
if images:
    # Save the first page as PNG
    images[0].save(output_image_path, "PNG")
    print(f"✅ Saved high-resolution page image to {output_image_path}")
else:
    raise Exception("No images generated from PDF.")

# ----- STEP 3: Build the Prompt for the Multimodal Model -----
# Here we craft a prompt that instructs the LLM to extract structured data,
# and we inform it that it has both a textual context and a visual input.
system_message = {
    "role": "system",
    "content": (
        "You are an expert in processing technical construction drawings. "
        "You will receive both a high-resolution image of a plumbing drawing page and a block of text extracted "
        "from that page. Your task is to extract structured information for each plumbing item present on the page. "
        "Extract the following information for each item: "
        "1. Item/Fixture Type (e.g., pipe & fittings, ductwork, electrical conduit, etc.), "
        "2. Quantity, "
        "3. Model Number or Specification Reference, "
        "4. Page Reference, "
        "5. Associated Dimensions (if any), "
        "6. Mounting Type (e.g., wall-hung, floor-mounted, etc. if stated). "
        "Return your response as valid JSON in the following schema:"
        "{\n  \"page\": <page number>,\n  \"items\": [\n    {\n      \"type\": \"...\",\n      \"quantity\": \"...\",\n      \"spec\": \"...\",\n      \"dimensions\": \"...\",\n      \"mounting\": \"...\"\n    },\n    ...\n  ]\n}\n\n"
        "Focus on the signal; use the textual context and the visual content together to disambiguate items and ignore extraneous details."
    )
}

# The user message includes both the contextual text and a note that an image is attached.
# Here, we're inserting a placeholder for the image content.
user_message = {
    "role": "user",
    "content": (
        f"Below is the contextual text extracted from page {page_number} of the plumbing drawing:\n\n"
        f"{context_text}\n\n"
        "In addition, a high-resolution image of the same page is attached. "
        "Please use both the text and the image to extract the structured information as per the instructions."
    )
}

# ----- STEP 4: Call the Multimodal LLM via OpenAI Client -----
# Note: The ability to send images to the ChatCompletion endpoint is available in GPT-4-Vision or similar models.
# The following code is illustrative. Replace or adapt it based on your actual API method for multimodal input.

response = openai.ChatCompletion.create(
    model="gpt-4.5-preview-2025-02-27",  # Use your multimodal model identifier
    messages=[system_message, user_message],
    # Here you would attach the image file if the API supports it; for example (pseudocode):
    # files=[{"file": open(output_image_path, "rb"), "purpose": "image"}]
)

# ----- STEP 5: Process and Print the Structured Output -----
structured_output = response.choices[0].message["content"]
print("✅ Structured Output from Multimodal LLM:")
print(structured_output)
