#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from appstore_data_agent.crew import AppstoreDataAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'indicative_developer_name': 'Sybo',
        'csv_file_path': 'game_center_games.csv',
        'topic': 'Analyze the scraped data and provide a report on the games'
    }
    
    try:
        AppstoreDataAgent().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
