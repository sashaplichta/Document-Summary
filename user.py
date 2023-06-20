class user():
    def __init__(self, username, name, password):
        self.name = name
        self.username = username
        self.password = password
        self.focus_areas = {}

    def set_focus(self, focus_areas):
        for focus in focus_areas:
            self.focus_areas[focus] = 0

    def update_focus(self, quiz_results):
        for question in quiz_results.keys():
            if quiz_results[question][2]:
                self.adjust_focus_helper(question, 1)
            else:
                self.adjust_focus_helper(question, -1)

    def adjust_focus_helper(self, text, valence):
        for focus in self.focus_areas.keys():
            self.focus_areas


        self.answers[question] = [self.questions[question], user_answer, response.choices[0]['text'].lower() == "yes"]