from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.developer_url_finder import DeveloperURLFinderTool
from .tools.app_store_scraper_tool import AppStoreScraperTool
from langchain_google_genai import ChatGoogleGenerativeAI
import os

@CrewBase
class AppstoreDataAgentCrew():
    """AppstoreDataAgent crew"""

    def __init__(self):
        # Initialize Gemini LLM
        # Ensure GEMINI_API_KEY is set in environment
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            verbose=True,
            temperature=0.5,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    @agent
    def app_store_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['app_store_researcher'],
            tools=[DeveloperURLFinderTool(), AppStoreScraperTool()],
            llm=self.llm,
            verbose=True
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
            llm=self.llm,
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.json'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AppstoreDataAgent crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

