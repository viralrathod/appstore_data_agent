#!/usr/bin/env python
import sys
from appstore_data_agent.crew import AppstoreDataAgentCrew

def run():
    """
    Run the crew.
    """
    # Example input: 'Voodo' or 'Nintendo'
    developer_name = sys.argv[1] if len(sys.argv) > 1 else 'Voodoo'
    
    inputs = {
        'developer_name': developer_name
    }
    
    try:
        result = AppstoreDataAgentCrew().crew().kickoff(inputs=inputs)
        print("\n\n########################")
        print("## Final Report JSON: ##")
        print("########################\n")
        print(result)
    except Exception as e:
        print(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    run()

