from crewai.flow.flow import Flow, listen, start, or_
from gerencia_ccr.crews.media_crew import MediaCrew
from dotenv import load_dotenv
from litellm import completion

import os
import json

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print(f"GOOGLE_API_KEY: {GOOGLE_API_KEY}")

class ProcessRequestFlow(Flow):
    model = "gpt-4o-mini"

    def __init__(self, request: str = None):
        super().__init__()
        self.request = request

    def categorize_pro(self, request: str = None):
        print("Triggered 'categorize_pro'")
        request_text = request or self.request

        response = completion(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that takes a client input for social media posts and categorizes it. Return a JSON file WITHOUT QUOTES and json word on it, with the following structure: {\"category\": \"<sermon_or_post-idea_or_bible-verse>\", \"sub_category\": \"<sub_category>\", \"require_development\": <true_or_false>, \"bible_verse\": <verse_or_empty-string>}.",
                },
                {
                    "role": "user",
                    "content": request_text,
                },
            ],
        )

        category = response["choices"][0]["message"]["content"]
        print(f"Category: {category}")

        return category

    def develop_idea(self, request: str = None):
        print("Triggered 'develop_idea'")
        request_text = request or self.request

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful assistant with great knowledge of biblical content. Develop a social media post concept based on {request_text}""",
                },
            ],
        )

        response_develop = response["choices"][0]["message"]["content"]
        print(f"Response develop: {response_develop}")

        return response_develop

    def extract_bible_verse(self, content):
        print("Triggered 'extract_bible_verse'")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful assistant with great knowledge of biblical content. Provide a biblical verse based on {content}""",
                },
            ],
        )

        response_verse = response["choices"][0]["message"]["content"]
        print(f"Response verse: {response_verse}")

        return response_verse

    def generate_post(self, content, sub_category, bible_verse):
        print("Triggered 'generate_post'")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful assistant with great knowledge of biblical content and social media management. Generate a social media post based on the 
                    theme: {sub_category}, 
                    the content: {content} and 
                    the biblical verse: {bible_verse}.
                    Make is short and to the point but engaging. Try to include a call for action.
                    Always respond in Portuguese (PT-PT). 
                    DO NOT use markdown on response, use pure text.""",
                },
            ],
        )

        response_post = response["choices"][0]["message"]["content"]
        print(f"Response post: {response_post}")

        return response_post

    @start()
    def categorize(self, request: str = None):
        print("Triggered 'categorize'")
        request_text = request or self.request

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that takes a client input for social media posts and categorizes it. Return a JSON file WITHOUT QUOTES and json word on it, with the following structure: {\"category\": \"<sermon_or_post-idea_or_bible-verse>\", \"sub_category\": \"<sub_category>\", \"require_development\": <true_or_false>, \"bible_verse\": <verse_or_empty-string>}.",
                },
                {
                    "role": "user",
                    "content": request_text,
                },
            ],
        )

        category = response["choices"][0]["message"]["content"]
        print(f"Category: {category}")

        return category

    @listen(or_(categorize, categorize_pro))
    def check_categorization(self, category):
        print("Triggered 'check_categorization'")
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""Check if the content on {self.request} is correctly categorized as {category}. Return a JSON file WITHOUT QUOTES and json word on it, with the following structure: {{"correct": true}} or {{"correct": false}}.""",
                },
            ],
        )

        response_check = response["choices"][0]["message"]["content"]
        print(f"Response check: {response_check}")

        return category, response_check

    @listen(check_categorization)
    def process_request(self, result):
        print("Processing request with result:", result)
        category, response_check = result
        response_check = json.loads(response_check)
        
        print("Category check response:", response_check)
        if not response_check["correct"]:
            print("Incorrect categorization, recategorizing request...")
            self.categorize_pro(self.request)
            return

        category = json.loads(category)
        print("Parsed category:", category)
        
        if category["require_development"]:
            print("Development required, developing idea...")
            developed_idea = self.develop_idea(self.request)
        else:
            print("No development required, using original request")
            developed_idea = self.request
        
        if category["bible_verse"] == "":
            print("No bible verse provided, extracting from developed idea...")
            bible_verse = self.extract_bible_verse(developed_idea)
        else:
            print("Using provided bible verse:", category["bible_verse"])
            bible_verse = category["bible_verse"]

        print("Generating post with developed idea and bible verse...")
        post = self.generate_post(developed_idea, category["sub_category"], bible_verse)
        print("\n\n============================= POST PRE PROCESSED =============================")
        print(post)
        print("============================= POST PRE PROCESSED =============================\n\n")

        result = {
            "content": {
                "developed_idea": developed_idea,
                "category": category["sub_category"],
                "bible_verse": bible_verse,
                "post": post
            }
        }
        
        final_result = MediaCrew().media_crew().kickoff(inputs=result)

        print("\n\n============================= PROCESSED =============================")
        print(final_result)
        print("============================= PROCESSED =============================\n\n")
