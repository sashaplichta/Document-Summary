from pdfminer.high_level import extract_text
from nltk.tokenize import blankline_tokenize

class document():
    def __init__(self, text):
        self.text = text

    def set_title(self, title):
        self.title = title

class preprocessor():
    def __init__(self, min_par_length=600):
        self.min_par_length = min_par_length

    def split_document(self, pdf_file):
        text = extract_text(pdf_file)
        paragraphs = blankline_tokenize(text)
        text = [paragraph for paragraph in paragraphs if len(paragraph) > self.min_par_length]
        
        return document(text)
