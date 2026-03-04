import logging
import fitz


logger = logging.getLogger("flagtech.extractor")

def load_pdf(file):
    file_name = getattr(file, "filename", "unknown")
    file.file.seek(0)
    pdf_bytes = file.file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    logger.info("Loaded PDF file=%s bytes=%s pages=%s", file_name, len(pdf_bytes), len(doc))
    return doc

def extract_text_from_pdf(file):
    """Extract raw text from a PDF file."""
    file_name = getattr(file, "filename", "unknown")
    doc = load_pdf(file)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    logger.info("Extracted text file=%s chars=%s", file_name, len(text))
    return text

def extract_words_from_pdf(file):
    """Extract words with positions from a PDF file, organized by page."""
    file_name = getattr(file, "filename", "unknown")
    doc = load_pdf(file)
    pages = []
    for page_num, page in enumerate(doc):
        page_rect = page.rect
        words = page.get_text("words")  # Returns list of (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        page_words = []
        for word in words:
            page_words.append({
                "x0": word[0],
                "y0": word[1],
                "x1": word[2],
                "y1": word[3],
                "text": word[4]
            })
        pages.append({
            "words": page_words,
            "width": page_rect.width,
            "height": page_rect.height
        })
    doc.close()
    word_count = sum(len(page.get("words", [])) for page in pages)
    logger.info("Extracted words file=%s pages=%s words=%s", file_name, len(pages), word_count)
    return pages