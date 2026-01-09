import pdfplumber
from PIL import Image
import pytesseract


def extract_text_from_pdf(file):
    # Ensure file pointer is at start
    try:
        file.file.seek(0)
    except Exception:
        pass

    texts = []
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                texts.append(text)
                continue

            # Fallback: render page to image and OCR
            try:
                img = page.to_image(resolution=200).original
                ocr_text = pytesseract.image_to_string(img)
                if ocr_text and ocr_text.strip():
                    texts.append(ocr_text)
            except Exception:
                # If rendering or OCR fails, skip this page
                continue

    return "\n".join(texts)