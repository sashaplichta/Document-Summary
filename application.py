import os
import json
import openai
from chat import chat
from preprocess import preprocessor

class application():
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.preprocessor = preprocessor()
        self.users = user_db() # instantiate user database
        # self.content = post_db() # instantiate post db
        self.questions = {}
        
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
            # self.get_quiz(docs[1])
            with open('quiz.txt', 'r') as fh:
                self.questions = json.loads(fh.read())
            results = self.give_quiz()

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
        # self.past_questions = [] # this is local and we do nothing with it so not sure what the point is
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

    def get_dummy_docs(self):
        with open('original_text.txt', "r") as fh:
            hard = fh.read()
        with open('eli5_level_text.txt', "r") as fh:
            easy = fh.read()
        with open('uni_level_text.txt', "r") as fh:
            medium = fh.read()

        return [easy, medium, hard]
    
    def display(self, text):
        print('\n' + text + '\n')
    
    def need_chat(self, results):
        if results[0] <= 0.6:
            return True
        return False
    
    def extract_tags(self, results):
        return results[1]

# ------------------------- Quiz Handling ------------------------- 

    def get_quiz(self, text):
        # print("generating quiz")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt= "Generate 5 questions and answers based on the text following the colon. The questions and answers pairs should all be outputted in a python dictionary in the form {\"Question\" : \"Answer\"}. These answers must be what you consider to be ideal for the given question. Do not label anything - the entirety of your response should be a python dictionary: " + text,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        with open('quiz.txt', "w") as fh:
            fh.write(response.choices[0]['text'])
        self.questions = json.loads(response.choices[0]['text'])
        # return response.choices[0]['text']

    def give_quiz(self): #answers is placeholder atm
        self.answers = {}
        cur_score = 0
        for question in self.questions.keys():
            print(question + '\n')
            user_answer = input("Your Answer: ")

            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="Do the following two sentences contain similar, and non-contradictory, statements: \"" + user_answer + "\" and \"" + self.questions[question] + "\"? Answer using exactly one word, either yes or no", 
                temperature=1,
                max_tokens=10,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            self.answers[question] = [self.questions[question], user_answer, response.choices[0]['text'].rstrip().lower() == "yes"]
            if (response.choices[0]['text'].lower() == "yes"):
                cur_score += 1
        
        return [cur_score / len(self.questions.keys()), self.get_worst_tags(self.answers)]
    
    def get_worst_tags(self, scores):
        wrong = ''
        for question in scores.keys():
            if not scores[question][2]:
                wrong += scores[question][0]

        response = openai.Completion.create(
                model="text-davinci-003",
                prompt="What two subjects does this list of sentences have most in common? Answer in the form of a Python list of the structure [\"Subject1\", \"Subject2\"] with no additional text: " + wrong, 
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        tags = response.choices[0]['text'].strip('][').split(', ')
        return tags

# ------------------------- Database mimic code classes -------------------------

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