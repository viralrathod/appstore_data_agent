from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.intent_identifier import DeveloperNameFuzzyIdentifierTool
from .tools.custom_tool import GameAppInfoScraperTool
from .tools.csv_reader_tool import CSVReaderTool
from .tools.developer_url_finder import DeveloperURLFinderTool
from textwrap import dedent

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AppstoreDataAgent():
    """AppstoreDataAgent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            tools=[DeveloperNameFuzzyIdentifierTool(), DeveloperURLFinderTool(), GameAppInfoScraperTool()]
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True,
            tools=[CSVReaderTool()]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def identify_developer_name(self) -> Task:
        return Task(
            config=self.tasks_config['identify_developer_name'],
            inputs={
                'indicative_developer_name': 'Voodoo'
            },
            agent=self.researcher(),
            # tools=[DeveloperNameFuzzyIdentifierTool()], # We are probably better off using Gemini Flash directly instead of using llama2 via ollama locally
            expected_output='A string representing the full and correct game developer name on the Apple App Store, e.g., "Nintendo Co., Ltd.", or "N/A" if not found. This output will be used as input for the next task.'
        )

    @task
    def find_developer_url(self) -> Task:
        return Task(
            config=self.tasks_config['find_developer_url'],
            agent=self.researcher(),
            # tools=[DeveloperURLFinderTool()], # We are probably better off depending on Gemini Flash directly instead using the googlesearch api to find the URL
            context=[self.identify_developer_name()],
            expected_output='A string representing an Apple App Store URL for a game by the identified developer, or "N/A" if no URL is found.'
        )

    @task
    def scrape_game_info(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_game_info'],
            agent=self.researcher(),
            tools=[GameAppInfoScraperTool()],
            context=[self.identify_developer_name(), self.find_developer_url()],
            expected_output='A string indicating the success or failure of scraping and CSV file creation, including the name of the generated CSV file.'
        )

    @task
    def generate_report(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            agent=self.reporting_analyst(),
            context=[self.scrape_game_info()],
            output_file='report.md',
            expected_output=dedent("""
                A markdown file named report.md containing a comprehensive report based on the scraped game data.
                The report MUST analyze the data from 'game_center_games.csv'.
                It should include:
                - An overview of the developer's games.
                - Key metrics (ratings, size, price, genre).
                - Game Center integration details (achievements, leaderboards).
                - Comparative analysis between free and paid games.
                - Any notable trends or observations.
                Do not use '```' in the report.
            """)
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AppstoreDataAgent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=[self.researcher(), self.reporting_analyst()],
            tasks=[
                self.identify_developer_name(),
                self.find_developer_url(),
                self.scrape_game_info(),
                self.generate_report()
            ],
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
