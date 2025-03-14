from tinydb import TinyDB, Query
import threading
import time
from googlesheetfetcher import process_responses
import config
import generate_questions
class MainPipeline:
    def __init__(self,interval=180):
        """
        :param db_path: Path to your TinyDB JSON file.
        :param question_func: Function that processes a row missing 'questions'.
                              Should accept a row dict and return a string.
        :param eval_func: Function that processes a row with both 'questions' and 'answers'.
                          Should accept a row dict and return a dict with keys 'eval' and 'score'.
        :param interval: Time interval between checks in seconds (default is 180 seconds).
        """
        self.db = TinyDB(config.DATABASE_FILE)
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        """Starts the background pipeline."""
        self.running = True
        self.thread = threading.Thread(target=self.run_pipeline, daemon=True)
        self.thread.start()

    def stop(self):
        """Stops the pipeline gracefully."""
        self.running = False
        if self.thread:
            self.thread.join()

    def run_pipeline(self):
        """Main loop that periodically checks the database."""
        while self.running:
            self.check_sheets()
            self.check_missing_questions()
            self.check_complete_entries()
            time.sleep(self.interval)

    def check_missing_questions(self):
        """
        Looks for rows where the 'questions' field is empty,
        runs the question_func on each row, and updates the database.
        """
        Q = Query()
        # Adjust the search criteria if your definition of "empty" is different.
        results = self.db.search(Q.questions == "")
        for row in results:
            print("Hunyaaa~")
            new_question = self.question_func(row)
            # Update the row using the primary key 'phone_number'
            self.db.update({'questions': new_question}, Q.phone_number == row.get('phone_number'))

    def check_complete_entries(self):
        """
        Looks for rows where 'answers' is filled and 'questions' is filled.
        Runs the eval_func on each row and updates the 'eval' and 'score' fields.
        """
        Q = Query()
        results = self.db.search((Q.answers != "") & (Q.questions != ""))
        for row in results:
            result_dict = self.eval_func(row)
            # We assume result_dict contains keys 'eval' and 'score'
            self.db.update(
                {
                    'eval': result_dict.get('eval'),
                    'score': result_dict.get('score')
                },
                Q.phone_number == row.get('phone_number'))
            
    def eval_func(self,row):

        return {
            'eval':"Humu humu!",
            'score':"8.9"
        }

    def question_func(self):
        Q = Query()
        """Generates questions based on given cv/resume."""
        results = self.db.search(Q.questions == "")
        for row in results:
            extracted_text = row.get('Resume/CV').get('extracted_text')
            position = row.get('posisi_yang_diinginkan')
            
            response = generate_questions.create_interview_question(extracted_text,position)
    
            question = response
            self.db.update({'question': question}, Q.phone_number == row.get('phone_number'))

    def check_sheets(self):
        process_responses()


class AnswerPipeline:
    def __init__(self,interval=180):
        self.db = TinyDB(config.DATABASE_FILE)
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        """Starts the background pipeline."""
        self.running = True
        self.thread = threading.Thread(target=self.run_pipeline, daemon=True)
        self.thread.start()

    def stop(self):
        """Stops the pipeline gracefully."""
        self.running = False
        if self.thread:
            self.thread.join()

    def run_pipeline(self):
        """Main loop that periodically checks the database."""
        while self.running:
            self.eval_func()
            time.sleep(self.interval)

    def eval_func(self,row):
        """Evaluates the answers based on the questions and the cv/resume."""
        questions = row.get('questions')
        answers = row.get('answers')
        prompt = f"""
        Evaluate the following answers based on the questions and the cv/resume:
        Questions: {questions}
        Answers: {answers}
        """ # [Chuck notes: prompt engineering needed]
        response = self.prompt_sender.send_prompt(prompt) # [Chuck notes: structured response needed]
        # Your evaluation logic here
        return {
            'eval':"Humu humu!",
            'score':"8.9"
        }

