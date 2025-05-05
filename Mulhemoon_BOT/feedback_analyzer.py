from telegram import User
from Users import Users
from Slides import Slides
from openai import OpenAI
from databasemanager import DatabaseManager
import requests
import json
import Levenshtein
import matplotlib.pyplot as plt

class Answers:
    def __init__(self, name, description,organ):
        self.name = name
        self.description = description
        self.organ = organ

    def get_name(self):
        if "," in self.name:
            names = self.name.split(",")
            names = {name.strip().lower() for name in names}
            return names
        else:
            return {self.name.strip().lower()}
    def get_description(self):
        return self.description
    def get_organ(self):
        if "," in self.organ:
            organs = self.organ.split(",")
            organs = {organ.strip().lower() for organ in organs}
            return organs
        else:
            return {self.organ.strip().lower()}
class FeedbackAnalyzer:
    def __init__(self,answers=None):
        self.users = Users("test.db")
        self.slides = Slides("test.db")
        self.answers = answers
    def check_name(self,slide_name, threshold=.8):
        user_input = slide_name.strip().lower()
        correct_names = self.answers.get_name()
        similarity_ratios = [Levenshtein.ratio(user_input, correct_name.lower().strip()) for correct_name in correct_names]
        similarity = max(similarity_ratios)
        return similarity >= threshold
    def check_organ(self,organ_name, threshold=.8):
        user_input = organ_name.strip().lower()
        correct_organs = self.answers.get_organ()
        similarity_ratios = [Levenshtein.ratio(user_input, correct_organ.lower().strip()) for correct_organ in correct_organs]
        similarity = max(similarity_ratios)
        return similarity >= threshold

    def analyze_answer(self,description_answer):
        api_key = "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"
        student_answer = self.answers.get_description()
        correct_answer = description_answer
        prompt = f"""
            The student has written the following answer: "{student_answer}"
            The correct answer is: "{correct_answer}"

            Please evaluate the student's answer in the following way:

            Respond directly to the student in a friendly and encouraging tone.

            Present your feedback in Markdown format and don't write the word "markdown" in your answer. and don't write ``` in your answer.

            Structure your answer using bullet points.

            Give a score from 0 to 10, where 0 means no similarity and 10 means the answer is completely correct.

            Explain clearly why you gave that score.

            Highlight what the student did well.

            Mention any important points that were missing or need improvement.
            
            and if the student ask for help or need help, give a score of 0 and explain it according to the information in the correct answer.
                """
        client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        )
        try:
            completion = client.chat.completions.create(
            model="microsoft/mai-ds-r1:free",
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ]
            )
            if completion and completion.choices:
                return completion.choices[0].message.content
            else:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama3.2", "prompt": prompt},
                    stream=True
                )

                full_reply = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        full_reply += chunk.get("response", "")  

                return full_reply
        except Exception as e:
            return f"❌ An error occurred: {str(e)}"
    def overall_feedback(self,formatted_feedback):
        api_key = "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"

        prompt = f"""
                The following are detailed scores and feedback for a student based on 10 medical slides:

                {formatted_feedback}

                Please analyze the student's overall performance and write:
                - A friendly and constructive summary of the student's performance.
                - General advice to improve in the future.
                - Encouragement message.
                """
        client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        )
        try:
            completion = client.chat.completions.create(
            model="qwen/qwen3-30b-a3b:free",
            messages=[
                {
                "role": "user",
                "content":prompt
                }
            ]
            )
            if completion and completion.choices:
                return completion.choices[0].message.content
            else:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama3.2", "prompt": prompt},
                    stream=True
                )

                full_reply = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        full_reply += chunk.get("response", "")  

                return full_reply
        except Exception as e:
            return f"❌ An error occurred: {str(e)}"
    def development_feedback(self,user_id,now_feedback):
        last_feedback = self.users.get_last_feedback(user_id)
        prompt = f""" The following is the last feedback for the student:
                {last_feedback}
                The following is the current feedback for the student:
                {now_feedback}
                I want you to compare the two feedbacks and write:
                - What did the student do well in the current feedback?
                - What did the student do poorly in the current feedback?
                - Is the student improving in the current feedback?
                - How can the student improve in the future? """
        try:
            response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama3.2", "prompt": prompt},
                    stream=True
                )

            full_reply = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    full_reply += chunk.get("response", "")  

                return full_reply
        except Exception as e:
            return f"❌ An error occurred: {str(e)}"
    def get_line_chart(self, user_id):
        scores = self.users.get_scores_dataframe(user_id)
        if scores is not None and not scores.empty:
            fig = plt.figure()
            plt.plot(scores['date'], scores['Correct name scores'], marker='o', label='Name Score')
            plt.plot(scores['date'], scores['Correct organ scores'], marker='s', label='Organ Score')
            plt.xlabel('Date')
            plt.ylabel('Score')
            plt.title('Scores Over Time')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            return fig.savefig('scores_chart.png')
