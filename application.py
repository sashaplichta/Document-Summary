import os
import openai
# from reportlab.pdfgen.canvas import Canvas
from pdfminer.high_level import extract_text
from nltk.tokenize import blankline_tokenize

class application():
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.preprocessor = preprocessor()
        self.users = user_db() # instantiate user database
        # self.content = post_db() # instantiate post db
        
        self.junk_encoding = {'Hard' : 2, 'Original' : 2, 'Hard/Original' : 2, 'Medium' : 1, 'Easy' : 0}

    def run(self):
        self.cur_user = input("Username: ")
        user_pass = input("Password: ")

        if (self.users.authenticate(self.cur_user, user_pass)): # some function to check if username/password is right
            # self.data = self.post_db.dbcall(self.cur_user) # get users data from post db
            
            cur_difficulty = input("What difficulty would you like to view your document?\nEasy, Medium, Hard/Original: ")
            # self.cur_document = self.data.keys()[0] 
            # cur_doc_original, cur_doc_uni, cur_doc_eli5 = self.get_documents(self.cur_document)
            # self.display(self.data[self.cur_document])
            docs = self.get_dummy_docs()
            self.display(docs[self.junk_encoding[cur_difficulty]])
            next = input("Proceed to quiz or view another difficulty? (Enter Quiz or Easy/Medium/Hard): ")

            while (next != 'Quiz'):
                self.display(docs[self.junk_encoding[next]])
                next = input("Proceed to quiz or view another difficulty? (Enter Quiz or Easy/Medium/Hard): ")

            # launch quiz
            # to be implemented
            results = (0.4, ["eye structure", "experimental design"])

            # launch chat
            if self.need_chat(results):
                cur_chat = chat()
                cur_chat.start_chat(self.extract_tags(results))

            print("Congratulations! It looks like you have a good understanding!")

        else:
            print("Sorry, wrong password")

    # pdf_file as string name of pdf if local -- gotta figure something else out otherwise
    def get_documents(self, pdf_file):
        self.raw_pdf = pdf_file
        self.pdf_text = self.preprocessor.split_document(pdf_file)[0:2]

        self.uni_level_text = '\n'.join(self.get_uni_version(self.pdf_text))
        self.eli5_text = self.get_eli5_version(self.uni_level_text) # collapse the previous level and create a high level summary
        self.uni_level_doc = self.to_pdf(self.uni_level_text)
        self.eli5_doc = self.to_pdf(self.eli5_text)
        self.past_questions = [] # this is local and we do nothing with it so not sure what the point is
        return (self.pdf_text, self.uni_level_doc, self.eli5_doc)

    def get_uni_version(self, pdf_text):
        print("running uni version")
        uni_version = []
        for paragraph in pdf_text:
            print('running paragraph')
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="Using an academic tone, summarize the text at the technical level of an upper year university student: " + paragraph,
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
    
    def get_dummy_docs(self):
        with open('original_text.txt', "r") as fh:
            hard = fh.read()
        with open('eli5_level_text.txt', "r") as fh:
            easy = fh.read()
        with open('uni_level_text.txt', "r") as fh:
            medium = fh.read()

        return [easy, medium, hard]
    
    def display(self, text):
        print(text)
    
    def need_chat(self, results):
        if results[0] <= 0.6:
            return True
        return False
    
    def extract_tags(self, results):
        return results[1]

# ------------------------- Document and preprocessor code classes ------------------------- 

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

# ------------------------- Chat code class ------------------------- 

class chat():
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.chat_log = {'GPT' : [],
                         'User' : []}
    
    def start_chat(self, missed_tags):
        output = ("It looks like you missed a couple questions. Since most had to do with " 
                + missed_tags[0] + " and " + missed_tags[1] 
                + ", I'm here to give you a quick overview and help clear up any misunderstanding.")

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=("Tell me a little bit about " + missed_tags[0] + " and " + missed_tags[1] + 
                    ". If I make any mistakes during our conversation, please correct me."),
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        output_tail = "\nDo you have any questions?"
        self.chat_log['GPT'].append(output + '\n' + response.choices[0]['text'] + output_tail)
        print(output + '\n' + response.choices[0]['text'] + output_tail)
        
        user_input = input("User: ")
        self.chat_log['User'].append(user_input)

        while(user_input != 'end chat'):
            alternated_log = self.alternate(self.chat_log)
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=alternated_log,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            self.display_response(response.choices[0]['text'])
            user_input = input("User: ")

            self.chat_log['GPT'].append(response.choices[0]['text'])
            self.chat_log['User'].append(user_input)

    def alternate(self, log):
        return '\n'.join([item for pair in zip(log['GPT'], log['User'] + [0])
                                 for item in pair])

    def display_response(self, response):
        print(response)

# ------------------------- Database code classes -------------------------

class user_db():
    def __init__(self):
        self.data = {'John' : '123abc'}

    def authenticate(self, username, password):
        if self.data[username] == password:
            return True
        return False

class post_db():
    def __init__(self):
        self.data = {}



app = application()
app.run()
# app.get_documents('redlight.pdf')

# print(app.eli5_text)
# print(app.get_quiz(app.uni_level_text))
# print(app.process_quiz(['Yes', 'no', 'maybe', 'photons', 'Si' ]))
# print(len(app.pdf_text))

# with open('original_text.txt', "w") as fh:
#     fh.write(app.pdf_text)
# with open('eli5_level_text.txt', "w") as fh:
#     fh.write(app.eli5_doc)
# with open('uni_level_text.txt', "w") as fh:
#     fh.write(app.uni_level_doc)
