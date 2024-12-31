# crew.py

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from crewai_tools import SerperDevTool
from pydantic import BaseModel
from typing import List
import yaml
import json

# Load environment variables
load_dotenv()

# Initialize the search tool
search = SerperDevTool(
    search_url="https://google.serper.dev/search",
    n_results=2,
)

# Existing Pydantic models for the main listing
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

# --- NEW MODELS BELOW ---

class Publication(BaseModel):
    title: str
    summary: str

class Project(BaseModel):
    name: str
    description: str

class SpecificProfessorInfo(BaseModel):
    """
    For deeper professor/lab research.
    """
    publications: List[Publication]
    projects: List[Project]
    courses: List[str]

class CoverLetterOutput(BaseModel):
    """
    For email subject/body + cover letter.
    """
    email_subject: str
    email_body: str
    cover_letter: str

# Paths to YAML configs
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

    @agent
    def deeper_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['deeper_researcher'],
            verbose=True,
            tools=[search]
        )

    @agent
    def cover_letter_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['cover_letter_agent'],
            verbose=True,
            tools=[]
        )

    @task
    def research_task(self) -> Task:
        # The main listing of professors/labs
        t = Task(
            config=self.tasks_config['research_task'],
            tools=[search],
        )
        # Ensure JSON matches ResearchInfo model
        t.output_json = ResearchInfo
        return t

    @task
    def professor_research_task(self) -> Task:
        """
        Deeper research on a single professor/lab.
        We'll just pass the professor name & URL as input.
        """
        t = Task(
            config=self.tasks_config['professor_research_task'],
            tools=[search],
        )
        # Now enforce the SpecificProfessorInfo model
        t.output_json = SpecificProfessorInfo
        return t

    @task
    def cover_letter_task(self) -> Task:
        """
        Takes the student's resume + professor/lab details, 
        returns a JSON with email_subject, email_body, cover_letter.
        """
        t = Task(
            config=self.tasks_config['cover_letter_task'],
        )
        # Enforce the CoverLetterOutput model
        t.output_json = CoverLetterOutput
        return t

    @crew
    def crew(self) -> Crew:
        """Creates the LatestAiDevelopment crew"""
        return Crew(
            agents=[
                self.researcher(),
                self.deeper_researcher(),
                self.cover_letter_agent(),
            ],
            tasks=[
                self.research_task(),
                self.professor_research_task(),
                self.cover_letter_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
