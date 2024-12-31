import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task
from crewai.task import Task as BaseTask
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

import yaml

# ------------------------------------------------------------------
# Load environment variables
load_dotenv()

# Load YAML configs
agents_config = 'config/agents.yaml'
tasks_config = 'config/tasks.yaml'

# ------------------------------------------------------------------
# Tools
search = SerperDevTool(
    search_url="https://google.serper.dev/search",
    n_results=2,
)

# ------------------------------------------------------------------
# Pydantic models
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

class ProfessorDetail(BaseModel):
    name: str
    biography: str
    notable_publications: List[str]
    research_focus: str

# ------------------------------------------------------------------
# Condition function for deeper research
def has_deeper_research_input(output: TaskOutput) -> bool:
    """
    Check if we have 'prof_name' in the inputs.
    If we do, run deeper_research_task. If not, skip.
    
    Important: This is NOT user input necessarily — 
    it can be set programmatically from the Flask route 
    after we figure out which professor was selected.
    """
    return bool(output.inputs.get("prof_name", ""))

# ------------------------------------------------------------------
@CrewBase
class LatestAiDevelopment_copy:
    """LatestAiDevelopment crew"""

    def __init__(self):
        self.agents_config = agents_config
        self.tasks_config = tasks_config

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
            tools=[search]
        )

    @agent
    def deeper_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["deeper_researcher"],
            verbose=True,
            tools=[search]
        )

    @task
    def research_task(self) -> Task:
        """
        Main research task -> fetch professors/labs.
        """
        task = Task(
            config=self.tasks_config["research_task"],
            tools=[search],
        )
        task.output_json = ResearchInfo
        return task

    @task
    def deeper_research_task(self) -> ConditionalTask:
        task = Task(
            config=self.tasks_config["deeper_research_task"],
            tools=[search],
        )
        task.output_json = ProfessorDetail
        return task

    @crew
    def crew(self) -> Crew:
        return Crew(
                    agents=[
                        self.deeper_researcher(),
                        
                    ],
                    tasks=[
                        self.deeper_research_task(),
                        
                    ],
                    process=Process.sequential,
                    verbose=True,
                )
