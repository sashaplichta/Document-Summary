import os
import openai
# from reportlab.pdfgen.canvas import Canvas
from pdfminer.high_level import extract_text
from nltk.tokenize import blankline_tokenize

class application():
    def __init__(self):
        openai.api_key = "" #key goes here
        self.preprocessor = preprocessor()

    # pdf_file as string name of pdf if local -- gotta figure something else out otherwise
    def get_documents(self, pdf_file):
        self.raw_pdf = pdf_file
        self.pdf_text = self.preprocessor.split_document(pdf_file)[0:2]
        self.uni_level_text = '\n'.join(self.get_uni_version(self.pdf_text))
        self.eli5_text = self.get_eli5_version(self.uni_level_text) # collapse the previous level and create a high level summary
        self.uni_level_doc = self.to_pdf(self.uni_level_text)
        self.eli5_doc = self.to_pdf(self.eli5_text)
        self.past_questions = []
        print(self.eli5_doc)

    def get_uni_version(self, pdf_text):
        print("running uni version")
        uni_version = []
        for paragraph in pdf_text:
            print('running paragraph')
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="""Using an academic tone, summarize the text at the technical level of an upper year university student: """ + paragraph,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            uni_version.append(response.choices[0]['text'])
        return uni_version
    
    def get_eli5_version(self, uni_text):
        print("running eli5 version")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Summarize the following text for a non-technical audience: " + uni_text,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0]['text']
    
    def to_pdf(self, text):
        print("running to pdf")
        title = openai.Completion.create(
            model="text-davinci-003",
            prompt="Write a title for the following text: " + text,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return title.choices[0]['text'] + '\n\n' + text
        # return {'title' : title,
        #         'body' : text}

    def get_quiz(self, text):
        print("generating quiz")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt= "Generate 5 questions and answers based on the scientific text proceeding the semicolon. The questions and answers pairs should all be coupled in a python list, and these question/answer lists must be in a python list. These answers must be what you consider to be ideal for the given question. Do not label anything - the entirety of your response should be a python list:" + text,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        self.past_questions.extend(response.choices[0]['text'])
        return response.choices[0]['text']

    def process_quiz(self, answers=[]): #answers is placeholder atm
        questions = self.past_questions[-1]
        print("generating quiz")
        for i in range(len(questions)):
            questions[i].append(answers[i])
        print(str(questions))
        print(str(answers))

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="The following is a python list of lists, index 0 of each a question, index 1 being the best answer to the question, and index 2 being an answer to the aforementioned question that you must grade, based on a comparison to the best answer and the answer's correctness" + str(questions), 
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        return response

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
        
        return result


app = application()
app.get_documents('redlight.pdf')
print(app.eli5_text)
print(app.get_quiz(app.uni_level_text))
print(app.process_quiz(['Yes', 'no', 'maybe', 'photons', 'Si' ]))