from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd

class CSVReaderToolInput(BaseModel):
    """Input schema for CSVReaderTool."""
    file_path: str = Field(..., description="The path to the CSV file to be read.")

class CSVReaderTool(BaseTool):
    name: str = "CSV Reader Tool"
    description: str = (
        "A tool to read the content of a CSV file and return it as a string."
    )
    args_schema: Type[BaseModel] = CSVReaderToolInput

    def _run(self, file_path: str) -> str:
        print(f"Reading CSV file: {file_path}")
        try:
            df = pd.read_csv(file_path)
            return df.to_csv(index=False)
        except FileNotFoundError:
            return f"Error: The file {file_path} was not found."
        except Exception as e:
            return f"Error reading CSV file {file_path}: {e}"
