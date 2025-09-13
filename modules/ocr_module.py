import os
from google.cloud import vision

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "..", "config", "google_ocr.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

def run_ocr(pdf_content: bytes) -> str:
    """Runs Google Vision OCR on PDF content and returns raw markdown text."""
    client = vision.ImageAnnotatorClient()

    input_config = vision.InputConfig(content=pdf_content, mime_type="application/pdf")
    features = [vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)]
    request = vision.AnnotateFileRequest(input_config=input_config, features=features)
    response = client.batch_annotate_files(requests=[request])

    output_md = []
    for i, page in enumerate(response.responses[0].responses):
        output_md.append(f"### Page {i + 1}\n")
        text = page.full_text_annotation.text
        lines = text.split("\n")

        in_table = False
        for line in lines:
            if any(char in line for char in ['|', '+', '-', '—', '│']):
                if not in_table:
                    output_md.append("```\n")
                    in_table = True
                output_md.append(line + "\n")
            else:
                if in_table:
                    output_md.append("```\n")
                    in_table = False
                output_md.append(line + "\n")

        if in_table:
            output_md.append("```\n")

    return "".join(output_md)
