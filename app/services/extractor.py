import fitz

def load_pdf(file):
    file.file.seek(0)
    pdf_bytes = file.file.read()
    return fitz.open(stream=pdf_bytes, filetype="pdf")

def extract_text_from_pdf(file):
    """Extract raw text from a PDF file."""
    doc = load_pdf(file)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_words_from_pdf(file):
    """Extract words with positions from a PDF file, organized by page."""
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
    return pages