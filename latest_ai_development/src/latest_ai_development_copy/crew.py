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
import json

# ------------------------------------------------------------------
# Load environment variables
load_dotenv()

# Load YAML configurations
# Adjust paths if needed
agents_config = 'config/agents.yaml'
tasks_config = 'config/tasks.yaml'

# ------------------------------------------------------------------
# Initialize the search tool
search = SerperDevTool(
    search_url="https://google.serper.dev/search",
    n_results=2,
)

# ------------------------------------------------------------------
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

# New model for deeper research
class ProfessorDetail(BaseModel):
    name: str
    biography: str
    notable_publications: List[str]
    research_focus: str

# ------------------------------------------------------------------
# Condition function for the deeper research
def is_professor_selected(output: TaskOutput) -> bool:
    """
    Checks if the user input includes a non-empty 'prof_name'.
    If True, run the deeper_research_task; otherwise, skip it.
    """
    # If there are multiple tasks in the chain, 'output.inputs' 
    # will carry forward your original kickoff inputs
    prof_name = output.inputs.get("prof_name", "")
    return bool(prof_name)

# ------------------------------------------------------------------
@CrewBase
class LatestAiDevelopment:
    """LatestAiDevelopment crew"""

    def __init__(self):
        """
        Load the config dictionaries so they can be referenced 
        in the agent/task decorators or in the methods.
        """
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
        """
        New agent that performs a deeper dive on a selected professor.
        """
        return Agent(
            config=self.agents_config["deeper_researcher"],
            verbose=True,
            tools=[search]
        )

    @task
    def research_task(self) -> Task:
        """
        Original broad research task.
        """
        task = Task(
            config=self.tasks_config["research_task"],
            tools=[search],
        )
        # Map the result to the Pydantic model
        task.output_json = ResearchInfo
        return task

    @task
    def deeper_research_task(self) -> ConditionalTask:
        """
        Conditional task that only runs if 'is_professor_selected' is True.
        The expected output is a deeper profile on a single professor.
        """
        task = ConditionalTask(
            config=self.tasks_config["deeper_research_task"],
            condition=is_professor_selected,  # The function that decides to run or skip
            agent=self.deeper_researcher(),   # Use the deeper_researcher agent
            output_json=ProfessorDetail,
        )
        return task

    @crew
    def crew(self) -> Crew:
        """Creates the LatestAiDevelopment crew"""
        return Crew(
            agents=[
                self.researcher(),
                self.deeper_researcher(),
            ],
            tasks=[
                self.research_task(),
                self.deeper_research_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )


if __name__ == "__main__":
    # For direct CLI testing
    crew_instance = LatestAiDevelopment().crew()
    result = crew_instance.kickoff(
        inputs={
            "topic": "Machine Learning",
            "university": "MIT",
            "prof_name": "Professor John Doe"  # If this is blank, deeper task will skip
        }
    )

    if result.pydantic:
        print("=== Final Structured Output ===")
        # result.pydantic might be a *list* of Pydantic objects if multiple tasks run
        # or a nested dictionary. This depends on your version of crewAI.
        print(result.pydantic.json(indent=2))
    else:
        print("=== Raw Output ===")
        print(result)
