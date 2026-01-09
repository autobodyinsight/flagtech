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


def extract_words_from_pdf(file):
    """Return a list of pages with width, height and words (text and boxes).

    Each page is a dict: {"width": w, "height": h, "words": [{"text": t, "x0":.., "x1":.., "y0":.., "y1":..}, ...]}
    """
    try:
        file.file.seek(0)
    except Exception:
        pass

    pages = []
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            w = page.width
            h = page.height
            words = []
            try:
                for wdict in page.extract_words():
                    # pdfplumber words use 'x0','x1','top','bottom'
                    text = wdict.get("text", "").strip()
                    if not text:
                        continue
                    x0 = float(wdict.get("x0", 0))
                    x1 = float(wdict.get("x1", 0))
                    y0 = float(wdict.get("top", 0))
                    y1 = float(wdict.get("bottom", 0))
                    words.append({"text": text, "x0": x0, "x1": x1, "y0": y0, "y1": y1})
            except Exception:
                # fallback: no words
                words = []

            pages.append({"width": w, "height": h, "words": words})

    return pages