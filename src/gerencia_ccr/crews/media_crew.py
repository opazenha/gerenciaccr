from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel, Field

import os

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print(f"GOOGLE_API_KEY: {GOOGLE_API_KEY}")

class PostModel(BaseModel):
    title: str = Field(..., description="Title of the post"),
    design: str = Field(..., description="Design of the post"),
    content: str = Field(..., description="Content of the post"),
    prompt: str = Field(..., description="VERY detailed prompt to be used on DALL-E for image generation")


@CrewBase
class MediaCrew():
    """MediaCrew for creating religious content for Instagram posts and stories"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        self.gemini_flash = LLM(
            model="gemini/gemini-1.5-flash"
        )
        self.gemini_pro = LLM(
            model="gemini/gemini-1.5-pro",
            api_key=GOOGLE_API_KEY,
            max_rpm=2
        )
        self.gpt_4o = LLM(
            model="gpt-4o"
        )
        self.gpt_4o_mini = LLM(
            model="gpt-4o-mini"
        )
        
    @after_kickoff
    def log_results(self, output):
        print("\n\n=== MediaCrew after kickoff ===")
        print(f"MediaCrew after kickoff: {output}")
        print("=== MediaCrew after kickoff ===\n\n")

        return output

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            llm=self.gpt_4o_mini,
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True
        )

    @agent
    def editor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['editor_agent'],
            llm=self.gemini_flash,
            verbose=True
        )

    @agent
    def bible_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['bible_expert'],
            llm=self.gemini_flash,
            verbose=True
        )

    @agent
    def summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config['summarizer'],
            llm=self.gemini_flash,
            verbose=True
        )

    @agent
    def instagram_stories_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['instagram_stories_agent'],
            llm=self.gemini_flash,
            verbose=True
        )

    @agent
    def instagram_posts_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['instagram_posts_agent'],
            llm=self.gemini_flash,
            verbose=True
        )

    @task
    def research(self) -> Task:
        task_config = self.tasks_config['research']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.research_agent()
        )

    @task
    def create_summary(self) -> Task:
        task_config = self.tasks_config['create_summary']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.summarizer()
        )

    @task
    def verify_biblical_content(self) -> Task:
        task_config = self.tasks_config['verify_biblical_content']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.bible_expert()
        )

    @task
    def create_caption(self) -> Task:
        task_config = self.tasks_config['create_caption']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.editor_agent(),
        )

    @task
    def create_instagram_story(self) -> Task:
        task_config = self.tasks_config['create_instagram_story']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.instagram_stories_agent(),
            output_format=PostModel,
            output_file=f"/posts/story_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"
        )

    @task
    def create_instagram_post(self) -> Task:
        task_config = self.tasks_config['create_instagram_post']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.instagram_posts_agent(),
            output_format=PostModel,
            output_file=f"/posts/post_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md",
        )

    @crew
    def media_crew(self) -> Crew:
        """Creates the MediaCrew that will generate content for Instagram stories and posts"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential
        )
