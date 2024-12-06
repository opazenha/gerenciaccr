from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

import os

@CrewBase
class IngestCrew():
    """IngestCrew for processing and categorizing religious content"""

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

    def receiver_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['receiver_agent'],
            allow_delegation=True,
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

    @crew
    def ingest_crew(self) -> Crew:
        """Creates the IngestCrew for content processing"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.hierarchical,
            manager_agent=self.receiver_agent()
        )
