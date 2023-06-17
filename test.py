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
pdf_file = 'redlight.pdf'
paragraphs = extract_paragraphs(pdf_file)

# Print out the extracted paragraphs
for i, paragraph in enumerate(paragraphs):
    if (len(paragraph) > 600):
        print(f"Paragraph {i+1}:")
        print(paragraph)
        print()

# import PyPDF2

# def extract_paragraphs(pdf_file):
#     # Open the PDF file
#     with open(pdf_file, 'rb') as file:
#         # Create a PDF reader object
#         reader = PyPDF2.PdfFileReader(file)

#         # Initialize an empty string to hold the extracted text
#         text = ''

#         # Iterate over the pages in the PDF and extract the text from each one
#         for i in range(reader.getNumPages()):
#             page = reader.getPage(i)
#             text += page.extractText()

#     # Split the text into paragraphs based on two consecutive line breaks
#     paragraphs = text.split('\n\n')

#     return paragraphs

# # Use the function on a specific PDF file
# pdf_file = 'redlight.pdf'
# paragraphs = extract_paragraphs(pdf_file)

# # Print out the extracted paragraphs
# for i, paragraph in enumerate(paragraphs):
#     print(f"Paragraph {i+1}:")
#     print(paragraph)
#     print()
