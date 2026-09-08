import io
import os
import pytesseract
from PIL import Image
import pdfplumber

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file)
    text = pytesseract.image_to_string(image)
    return text.strip()

def extract_text_from_pdf(uploaded_file):
    data = uploaded_file.read()
    text_parts = []

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)

    return "\n\n".join(text_parts).strip()