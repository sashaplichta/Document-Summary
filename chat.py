import os
import openai

class chat():
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.chat_log = {'GPT' : [],
                         'User' : []}
    
    def start_chat(self, missed_tags):
        output = ("\nIt looks like you missed a couple questions. Since most had to do with " + missed_tags[0] + " and " + missed_tags[1] + ", I'm here to give you a quick overview and help clear up any misunderstanding.")

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
        self.chat_log['GPT'].append(output + response.choices[0]['text'] + output_tail)
        print(output + response.choices[0]['text'] + output_tail)
        
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
        if (response[0:2] == '\n'):
            print(response[4:])
        else:
            print(response)

# session = chat()
# session.start_chat(['large language models', 'neural networks'])

# with open('chatlog.txt', "w") as fh:
#     fh.write(session.alternate(session.chat_log))