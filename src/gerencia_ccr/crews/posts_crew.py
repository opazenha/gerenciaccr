from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import DallETool

import os

dalle_tool = DallETool(model="dall-e-3",
                       size="1024x1024",
                       quality="standard",
                       n=1)

@CrewBase
class PostsCrew():
    """PostsCrew for processing and categorizing religious content"""

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

    

    @crew
    def posts_crew(self) -> Crew:
        """Creates the PostsCrew for content processing"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequencial,
        )
