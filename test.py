# from pathlib import Path
# import fitz

# for file_path in Path.cwd().glob("*.pdf"):
#     doc = fitz.open(file_path)

# # toc = doc.metadata
# toc = doc.get_toc()
# print(toc)

# print(Path.cwd())
# print(fitz.__doc__)

from pdfminer.high_level import extract_text
from nltk.tokenize import blankline_tokenize

def extract_paragraphs(pdf_file):
    # Extract text from the PDF
    text = extract_text(pdf_file)

    # Use NLTK to split the text into paragraphs
    # Note: This assumes that paragraphs are separated by blank lines.
    # You may need to adjust this depending on the formatting of your specific documents.
    paragraphs = blankline_tokenize(text)

    return paragraphs

# Use the function on a specific PDF file
pdf_file = 'path_to_your_pdf_file.pdf'
paragraphs = extract_paragraphs(pdf_file)

# Print out the extracted paragraphs
for i, paragraph in enumerate(paragraphs):
    print(f"Paragraph {i+1}:")
    print(paragraph)
    print()