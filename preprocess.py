from pdfminer.high_level import extract_text
from nltk.tokenize import blankline_tokenize

class document():
    def __init__(self, text, raw_doc):
        self.text = text
        self.raw = raw_doc

    def set_title(self, title):
        self.title = title

class preprocessor():
    def __init__(self, min_par_length=600):
        self.min_par_length = min_par_length

    def split_document(self, pdf_file):
        text = extract_text(pdf_file)
        paragraphs = blankline_tokenize(text)

        result = []
        for paragraph in paragraphs:
            if len(paragraph) > self.min_par_length:
                result.append(paragraph.replace("\n", ""))
        
        return document(result, pdf_file)

pre = preprocessor()
doc = pre.split_document('redlight.pdf')
for x in doc.text[0:2]: print(x + '\n')