from Users import Users
from Slides import Slides
from openai import OpenAI
from databasemanager import DatabaseManager
import requests
import json
import Levenshtein

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
    def check_name(self,slide_name, threshold=.7):
        user_input = slide_name.strip().lower()
        correct_names = self.answers.get_name()
        similarity_ratios = [Levenshtein.ratio(user_input, correct_name) for correct_name in correct_names]
        similarity = max(similarity_ratios)
        return similarity >= threshold
    def check_organ(self,organ_name, threshold=.7):
        user_input = organ_name.strip().lower()
        correct_organs = self.answers.get_organ()
        similarity_ratios = [Levenshtein.ratio(user_input, correct_organ) for correct_organ in correct_organs]
        similarity = max(similarity_ratios)
        return similarity >= threshold

answers = Answers("Bovine leukosis,Bl","abdullah","abdullah,mohamed")
feedback_analyzer = FeedbackAnalyzer(answers)
print(feedback_analyzer.check_name("boven leukosis"))
print(feedback_analyzer.check_organ("omar"))