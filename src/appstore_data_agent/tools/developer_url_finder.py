from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from googlesearch import search

class DeveloperURLFinderInput(BaseModel):
    """Input schema for DeveloperURLFinderTool."""
    developer_name: str = Field(..., description="The full name of the game developer.")

class DeveloperURLFinderTool(BaseTool):
    name: str = "Developer URL Finder Tool"
    description: str = (
        "Finds the Apple App Store URL for a given game developer's page using a web search."
    )
    args_schema: Type[BaseModel] = DeveloperURLFinderInput

    def _run(self, developer_name: str) -> str:
        query = f"{developer_name} app store developer page"
        try:
            for url in search(query, num_results=5):
                if "apps.apple.com" in url and "/developer/" in url:
                    return url
            return "N/A: No App Store Developer Page URL found."
        except Exception as e:
            return f"Error finding developer URL: {e}"

