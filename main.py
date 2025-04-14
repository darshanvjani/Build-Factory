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
        "You are a specialized estimator focused specifically on plumbing work packages from construction submittal PDFs. "
        "You'll be given a high-resolution plumbing drawing image and extracted contextual text from the same PDF page. "
        "Your task is to extract detailed structured data on all plumbing-related items visible or described.\n\n"

        "Return your response as strictly valid JSON using the schema below:\n"
        "{\n"
        "  \"page\": <page number>,\n"
        "  \"plumbing_items\": [\n"
        "    {\n"
        "      \"item_type\": \"<Specific plumbing item type (pipe, fitting, valve, fixture, equipment, etc.)>\",\n"
        "      \"quantity\": \"<Exact numeric quantity, avoid 'multiple' or unclear counts>\",\n"
        "      \"model_or_spec\": \"<Manufacturer Model Number, Part Number, or Spec Reference if available>\",\n"
        "      \"dimensions\": \"<Size, Diameter, Length, BE height, or other relevant dimensions>\",\n"
        "      \"mounting_type\": \"<Mounting or installation type (wall-hung, floor-mounted, ceiling, vertical riser, etc. if available)>\",\n"
        "      \"page_reference\": \"<Page number or drawing reference>\",\n"
        "      \"confidence\": \"<Confidence score between 0.0 (low) to 1.0 (high)>\",\n"
        "      \"notes\": \"<Brief notes ONLY if confidence is below 0.7 or if clarification needed else write N/A>\"\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"

        "### CRITICAL GUIDELINES:\n"
        "- Focus ONLY on plumbing-related items (pipes, fittings, valves, plumbing fixtures, drains, vents, risers, etc.). Ignore unrelated items such as electrical, structural, HVAC unless explicitly tied to plumbing work.\n"
        "- Provide exact quantities; visually count symbols from diagrams if needed. Do NOT generalize as 'multiple'. Provide an exact number or a best-estimate with notes.\n"
        "- Extract accurate spec references (e.g., HUH-9, OM-135, HHWR, HHWS, CWR). Include details even if only partially visible.\n"
        "- Carefully extract and clearly indicate dimensions like diameter (Ø), length, elevations (BE heights), etc., directly from annotations or tables.\n"
        "- Clearly identify the mounting method or location from text labels or visual symbols (wall-mounted, ceiling-hung, floor-mounted, vertical piping, horizontal suspended piping, risers).\n"
        "- Provide a confidence score (0.0 to 1.0) per item based on clarity, accuracy, and available evidence from both image and text.\n"
        "- Include concise notes ONLY if confidence is below 0.7 or when an estimated count or dimension is necessary due to unclear or partial information.\n\n"

        "Extracted data will be directly used for plumbing material estimation and fabrication, thus high accuracy and detailed extraction are essential.\n"
        "Respond only in the requested structured JSON format."
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

structured_output = response.choices[0].message["content"]
print("✅ Structured Output from Multimodal LLM:")
print(structured_output)
