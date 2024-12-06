from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import DallETool

import os

dalle_tool = DallETool(model="dall-e-3",
                       size="1024x1024",
                       quality="standard",
                       n=1)

@CrewBase
class MediaCrew():
    """MediaCrew for processing and categorizing religious content"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    # gemini_pro=LLM(
    #     model="gemini/gemini-1.5-pro",
    #     max_rpm=2
    # )

    def __init__(self):
        self.llm = LLM(
            model="gemini/gemini-1.5-flash"
        )

    @after_kickoff
    def log_results(self, output):
        print(f"Content Processing Results: {output}")
        return output

    def media_manager_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['media_manager_agent'],
            allow_delegation=True,
            llm=self.llm,
            verbose=True
        )

    @agent
    def receiver_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['receiver_agent'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def bible_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['bible_expert'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config['summarizer'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def instagram_stories_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['instagram_stories_agent'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def instagram_posts_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['instagram_posts_agent'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def designer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['designer_agent'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def image_creator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['image_creator_agent'],
            llm=self.llm,
            tools=[dalle_tool],
            verbose=True
        )

    @agent
    def editor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['editor_agent'],
            llm=self.llm,
            verbose=True
        )

    @task
    def classify_content(self) -> Task:
        task_config = self.tasks_config['classify_content']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.receiver_agent()
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
    def summarize_content(self) -> Task:
        task_config = self.tasks_config['create_summary']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.summarizer()
        )

    @task
    def create_instagram_story(self) -> Task:
        task_config = self.tasks_config['create_instagram_story']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.instagram_stories_agent()
        )

    @task
    def create_instagram_post(self) -> Task:
        task_config = self.tasks_config['create_instagram_post']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.instagram_posts_agent()
        )

    @task
    def generate_image_prompt(self) -> Task:
        task_config = self.tasks_config['generate_image_prompt']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.designer_agent()
        )

    @task
    def create_image(self) -> Task:
        task_config = self.tasks_config['create_image']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.image_creator_agent()
        )

    @task
    def create_caption(self) -> Task:
        task_config = self.tasks_config['create_caption']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.editor_agent()
        )

    @crew
    def media_crew(self) -> Crew:
        """Creates the MediaCrew for content processing"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.hierarchical,
            manager_agent=self.media_manager_agent()
        )
