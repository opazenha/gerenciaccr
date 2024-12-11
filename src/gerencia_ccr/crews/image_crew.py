from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import DallETool, SerperDevTool, ScrapeWebsiteTool

import os

dalle_tool = DallETool(model="dall-e-3",
                       size="1024x1024",
                       quality="standard",
                       n=1)

@CrewBase
class ImageCrew():
   """ImageCrew for processing and categorizing religious content"""

   agents_config = 'config/agents.yaml'
   tasks_config = 'config/tasks.yaml'

   def __init__(self):
      self.gemini_flash = LLM(
         model="gemini/gemini-1.5-flash"
      )
      self.gpt_4o = LLM(
         model="gpt-4o"
      )
      self.gpt_4o_mini = LLM(
         model="gpt-4o-mini"
      )

   @after_kickoff
   def log_results(self, output):
      print(f"Content Processing Results: {output}")
      return output

   @agent
   def designer_agent(self) -> Agent:
      return Agent(
         config=self.agents_config['designer_agent'],
         llm=self.llm,
         tools=[SerperDevTool(), ScrapeWebsiteTool()],
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

   @crew
   def image_crew(self) -> Crew:
      """Creates the ImageCrew for content processing"""
      return Crew(
         agents=self.agents,
         tasks=self.tasks,
         verbose=True,
         process=Process.hierarchical,
         manager_llm=self.gpt_4o_mini,
         planning=True,
         planning_llm=self.gpt_4o
      )