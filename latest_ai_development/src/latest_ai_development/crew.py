# crew.py

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from crewai_tools import SerperDevTool
from pydantic import BaseModel
from typing import List
from pathlib import Path
import yaml
import json
import datetime


# Load environment variables
load_dotenv()

# Initialize the search tool
search = SerperDevTool(
    search_url="https://google.serper.dev/search",
    n_results=2,
)

# Define Pydantic models
class Professor(BaseModel):
    name: str
    research_interests: str
    contact_email: str
    url: str

class Lab(BaseModel):
    name: str
    focus: str
    url: str

class ResearchInfo(BaseModel):
    professors: List[Professor]
    labs: List[Lab]

# Configuration file paths
agents_config = 'config/agents.yaml'
tasks_config = 'config/tasks.yaml'

@CrewBase
class LatestAiDevelopment():
    """LatestAiDevelopment crew"""

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            tools=[search]
        )

 

    @task
    def research_task(self) -> Task:
        task = Task(
            config=self.tasks_config['research_task'],
            tools=[search],
        )
        task.output_json = ResearchInfo
        return task

    @crew
    def crew(self) -> Crew:
        """Creates the LatestAiDevelopment crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,    # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

if __name__ == "__main__":
    crew_instance = LatestAiDevelopment()
    crew = crew_instance.crew()
    result = crew.kickoff()

    # Optionally, print the JSON output
    if result.pydantic:
        print(result.pydantic.json(indent=2))
