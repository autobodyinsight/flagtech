from app.services.extractor import extract_words_from_pdf
import sys

# Simulate uploading a file
pdf_path = sys.argv[1] if len(sys.argv) > 1 else "test.pdf"

class FakeFile:
    def __init__(self, path):
        self.path = path
    async def read(self):
        with open(self.path, 'rb') as f:
            return f.read()

# This won't work directly since extract_words requires an UploadFile
# Let me just check what's available
print("Available files:")
import os
for f in os.listdir('.'):
    if f.endswith('.pdf'):
        print(f"  {f}")

