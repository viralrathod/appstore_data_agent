from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import ollama

class DeveloperNameFuzzyIdentifierInput(BaseModel):
    """Input schema for DeveloperNameFuzzyIdentifierTool."""
    indicative_developer_name: str = Field(..., description="An indicative or partial name of a game developer, potentially with misspellings.")

class DeveloperNameFuzzyIdentifierTool(BaseTool):
    name: str = "Developer Name Fuzzy Identifier Tool"
    description: str = (
        "Identifies the full, correct game developer name on the Apple App Store based on an indicative or potentially misspelled name using Ollama."
    )
    args_schema: Type[BaseModel] = DeveloperNameFuzzyIdentifierInput

    def _run(self, indicative_developer_name: str) -> str:
        ollama.pull(model='llama2')
        prompt = f"Given the indicative game developer name \"{indicative_developer_name}\", what is the most likely full and correct game developer name as it appears on the Apple App Store? Only return the full name, without any other text. If no clear match is found, return 'N/A'. I repeat only return the full name and no other text. Example: Given the indicative game developer name \"Nintenddo\", the full and correct game developer name is \"Nintendo Co., Ltd.\""
        try:
            response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': prompt}])
            full_developer_name = response['message']['content'].strip()
            print(f"Full developer name: {full_developer_name}")
            return full_developer_name
        except Exception as e:
            return f"Error identifying developer name: {e}"
