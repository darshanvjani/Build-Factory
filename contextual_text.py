import re
import html
import json
from unstructured.partition.pdf import partition_pdf


def get_clean_contextual_text_from_page(pdf_path: str, poppler_path: str) -> str:
    """
    High-level function to extract and clean context-aware text from a single-page PDF.
    This includes:
    - Layout-aware partitioning using Unstructured
    - Logical sorting (top-to-bottom, left-to-right)
    - Cleanup of vertical/garbled characters and HTML/unicode
    """

    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        infer_table_structure=True,
        pdf2image_config={"poppler_path": poppler_path}
    )

    # Step 2: Sort elements by Y then X coordinates
    def get_coords(el):
        coords = el.metadata.coordinates
        if coords and coords.points:
            x, y = coords.points[0]
            return (round(y, 2), round(x, 2))
        return (9999, 9999)

    sorted_elements = sorted(
        [el for el in elements if el.text and el.metadata.coordinates and el.metadata.coordinates.points],
        key=get_coords
    )

    raw_merged = "\n".join(el.text.strip() for el in sorted_elements)

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

if __name__ == "__main__":
    pdf_path = r"output_pdfs\page_2.pdf"
    poppler_path = r"C:\Users\Janid\OneDrive\Temp\Release-24.08.0-0\poppler-24.08.0\Library\bin"

    elements, context_text = get_clean_contextual_text_from_page(pdf_path, poppler_path)

    with open("cleaned_contextual_text_page_2.json", "w") as f:
        json.dump({"page": 2, "contextual_text": context_text}, f, indent=2)


    print("✅ Cleaned contextual text saved!")
