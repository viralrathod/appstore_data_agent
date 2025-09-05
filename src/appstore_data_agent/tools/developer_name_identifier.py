from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import ollama

class DeveloperNameIdentifierInput(BaseModel):
    """Input schema for DeveloperNameIdentifierTool."""
    app_url: str = Field(..., description="The URL of the application on the Apple App Store.")

class DeveloperNameIdentifierTool(BaseTool):
    name: str = "Developer Name Identifier Tool"
    description: str = (
        "Identifies the full game developer name from an Apple App Store URL using Ollama."
    )
    args_schema: Type[BaseModel] = DeveloperNameIdentifierInput

    def _run(self, app_url: str) -> str:
        prompt = f"Extract the full game developer name from the following Apple App Store URL: {app_url}. Only return the name, without any other text."
        try:
            response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': prompt}])
            developer_name = response['message']['content'].strip()
            return developer_name
        except Exception as e:
            return f"Error identifying developer name: {e}"
