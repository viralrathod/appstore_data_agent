import pytest
from unittest.mock import patch, MagicMock
import ollama

# TODO: Fix this import
from src.appstore_data_agent.tools.intent_identifier import (
    DeveloperNameFuzzyIdentifierInput,
    DeveloperNameFuzzyIdentifierTool
)

@pytest.fixture
def mock_ollama_chat():
    with patch('ollama.chat') as mock_chat:
        yield mock_chat

def test_developer_name_fuzzy_identifier_input_valid():
    input_data = DeveloperNameFuzzyIdentifierInput(indicative_developer_name="Nintendo")
    assert input_data.indicative_developer_name == "Nintendo"

def test_developer_name_fuzzy_identifier_input_missing_field():
    with pytest.raises(ValueError):
        DeveloperNameFuzzyIdentifierInput() # Should raise error for missing field

def test_run_successful_identification(mock_ollama_chat):
    mock_ollama_chat.return_value = {
        'message': {'content': 'Nintendo Co., Ltd.'}
    }

    tool = DeveloperNameFuzzyIdentifierTool()
    result = tool._run(indicative_developer_name="Nintenddo")

    mock_ollama_chat.assert_called_once_with(
        model='llama2',
        messages=[{'role': 'user', 'content': "Given the indicative game developer name \"Nintenddo\", what is the most likely full and correct game developer name as it appears on the Apple App Store? Only return the full name, without any other text. If no clear match is found, return 'N/A'. I repeat only return the full name and no other text. Example: Given the indicative game developer name \"Nintenddo\", the full and correct game developer name is \"Nintendo Co., Ltd.\""}]
    )
    assert result == "Nintendo Co., Ltd."

def test_run_no_clear_match(mock_ollama_chat):
    mock_ollama_chat.return_value = {
        'message': {'content': 'N/A'}
    }

    tool = DeveloperNameFuzzyIdentifierTool()
    result = tool._run(indicative_developer_name="xyzcorp")

    assert result == "N/A"

def test_run_ollama_error(mock_ollama_chat):
    mock_ollama_chat.side_effect = Exception("Ollama API error")

    tool = DeveloperNameFuzzyIdentifierTool()
    result = tool._run(indicative_developer_name="Nintendo")

    assert "Error identifying developer name: Ollama API error" in result

