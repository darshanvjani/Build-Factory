import os
import openai
import base64
import json
from config import OPENAI_MODEL

def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded image string
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
        
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode('utf-8')

def extract_structured_data_from_plumbing_drawing(image_path: str, context_text: str, page_number: int, api_key: str, model: str = OPENAI_MODEL):
    """
    Calls the multimodal LLM using the OpenAI API interface.
    This function base64 encodes the image and sends it along with the contextual text
    in the messages. It returns the structured JSON response.
    
    Args:
        image_path (str): Path to the image file
        context_text (str): Extracted contextual text from the PDF
        page_number (int): Page number
        api_key (str): OpenAI API key
        model (str): OpenAI model to use (default: gpt-4-vision-preview)
        
    Returns:
        str: JSON response from the OpenAI API
    """
    if not api_key:
        raise ValueError("OpenAI API key is required")
        
    openai.api_key = api_key

    # Encode the image to base64
    try:
        base64_image = encode_image_to_base64(image_path)
    except Exception as e:
        raise Exception(f"Error encoding image: {str(e)}")

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

    # Use the OpenAI API call
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[system_message, user_message]
        )
        
        # Validate that the response is valid JSON
        content = response.choices[0].message.content
        try:
            json.loads(content)  # Just to validate it's proper JSON
            return content
        except json.JSONDecodeError:
            print(f"Warning: Response from OpenAI is not valid JSON for page {page_number}")
            return content
            
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract structured data from a plumbing drawing.')
    parser.add_argument('--image_path', required=True, help='Path to the image file')
    parser.add_argument('--context_text', required=True, help='Path to the context text file')
    parser.add_argument('--page_number', type=int, required=True, help='Page number')
    parser.add_argument('--api_key', required=True, help='OpenAI API key')
    parser.add_argument('--output_dir', default='output', help='Directory to save output files')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Read context text from file
    with open(args.context_text, 'r') as f:
        context_text = f.read()
    
    # Extract structured data
    structured_output = extract_structured_data_from_plumbing_drawing(
        image_path=args.image_path,
        context_text=context_text,
        page_number=args.page_number,
        api_key=args.api_key
    )
    
    # Save the structured output
    output_file = os.path.join(args.output_dir, f"structured_output_page_{args.page_number}.json")
    with open(output_file, 'w') as f:
        f.write(structured_output)
    
    print(f"✅ Structured output saved to {output_file}!")
