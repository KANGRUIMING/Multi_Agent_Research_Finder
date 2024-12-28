from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from crewai_tools import SerperDevTool
#from tools.custom_tool import CustomSerperDevTool


load_dotenv()

search = SerperDevTool(
	search_url="https://google.serper.dev/search",
    n_results=2,
)

#search_query="{topic} {university} research"



@CrewBase
class LatestAiDevelopment():
	"""LatestAiDevelopment crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[search]
			
		)


	@agent
	def chat_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['chat_agent'],
			verbose=True
		)


	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			tools=[search],
		)

	@task
	def chat_task(self) -> Task:
		return Task(
			config=self.tasks_config['chat_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the LatestAiDevelopment crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			#memory=True,
			#planning=True
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
