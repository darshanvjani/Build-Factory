import openai
import base64

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode('utf-8')

def extract_structured_data_from_plumbing_drawing(image_path: str, context_text: str, page_number: int, api_key: str, model: str = "gpt-4.5-preview-2025-02-27"):
    """
    Calls the multimodal LLM using the new API interface.
    This function base64 encodes the image and sends it along with the contextual text
    in the messages. It returns the structured JSON response.
    """
    openai.api_key = api_key

    # Encode the image to base64
    base64_image = encode_image_to_base64(image_path)

    # Build the system prompt (plumbing-specific and with confidence score)
    system_message = {
        "role": "system",
        "content": (
            "You are a specialized estimator focused specifically on plumbing work packages from construction submittal PDFs. "
            "You'll be given a high-resolution plumbing drawing image and extracted contextual text from the same PDF page. "
            "Your task is to extract detailed structured data on all plumbing-related items (e.g., pipes, fittings, valves, fixtures, drains, vents, risers) visible or described. \n\n"
            "Return your response as strictly valid JSON using the schema below:\n"
            "{\n"
            "  \"page\": <page number>,\n"
            "  \"plumbing_items\": [\n"
            "    {\n"
            "      \"item_type\": \"<Specific plumbing item type (pipe, fitting, valve, fixture, etc.)>\",\n"
            "      \"quantity\": \"<Exact numeric quantity>\",\n"
            "      \"model_or_spec\": \"<Manufacturer model number, part number, or specification reference if available>\",\n"
            "      \"dimensions\": \"<Relevant dimensions such as pipe size, diameter, BE height, length, etc.>\",\n"
            "      \"mounting_type\": \"<Mounting or installation type (wall-hung, ceiling-mounted, floor-mounted, vertical riser, etc.)>\",\n"
            "      \"confidence\": \"<Confidence score between 0.0 (low) and 1.0 (high)>\",\n"
            "      \"notes\": \"<Concise notes if confidence is below 0.7 or clarification is needed; otherwise 'N/A'>\"\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            "### CRITICAL GUIDELINES:\n"
            "- Focus ONLY on plumbing-related items (pipes, fittings, valves, plumbing fixtures, drains, vents, risers, etc.). Ignore unrelated items unless they are explicitly tied to the plumbing work.\n"
            "- Provide exact numeric quantities. Do not use vague terms such as 'multiple'. If an estimate is necessary, provide your best estimate with a note.\n"
            "- Extract accurate specification references (e.g., HUH-9, OM-135, HHWR, HHWS, CWR). Include details even if only partially visible.\n"
            "- Carefully extract dimensions (like diameter (Ø), length, BE heights, etc.) from annotations or tables.\n"
            "- Clearly determine and indicate the mounting type from labels or visual cues (e.g., wall-mounted, ceiling-mounted, floor-mounted, vertical).\n"
            "- Provide a confidence score (0.0 to 1.0) for each item based on the clarity and available evidence from both the image and text.\n"
            "- Include concise notes only if confidence is below 0.7 or if there is uncertainty.\n\n"
            "Extracted data will be used for plumbing material estimation and fabrication; high accuracy is essential. "
            "Respond only in the requested JSON format."
        )
    }

    # Build the user message including both text and the image in base64.
    user_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": (
                    f"Below is the contextual text extracted from page {page_number} of the plumbing drawing:\n\n"
                    f"{context_text}\n\n"
                    "Please analyze this text alongside the attached high-resolution image."
                )
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            }
        ]
    }

    # Use the new API call (note: for the new interface, use openai.chat.completions.create)
    response = openai.chat.completions.create(
        model=model,
        messages=[system_message, user_message]
    )

    return response.choices[0].message.content
