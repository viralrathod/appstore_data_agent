# tests/test_developer_url_finder.py

import pytest
from unittest.mock import patch, MagicMock
from googlesearch import search

from src.appstore_data_agent.tools.developer_url_finder import (
    DeveloperURLFinderInput,
    DeveloperURLFinderTool
)

# Mock HTML content

@pytest.fixture
def mock_google_search():
    with patch("googlesearch.search") as mock_search:
        yield mock_search

def test_developer_game_url_finder_input_valid():
    input_data = DeveloperURLFinderInput(developer_name="Nintendo Co., Ltd.")
    assert input_data.developer_name == "Nintendo Co., Ltd."

def test_developer_game_url_finder_input_missing_field():
    with pytest.raises(ValueError):
        DeveloperURLFinderInput() # Should raise error for missing field

def test_run_successful_url_finding(mock_google_search):
    mock_google_search.return_value = ["https://apps.apple.com/us/developer/nintendo-co-ltd/id123456789", "https://example.com"]

    tool = DeveloperURLFinderTool()
    result = tool._run(developer_name="Nintendo Co., Ltd.")

    mock_google_search.assert_called_once_with(
        "Nintendo Co., Ltd. app store developer page url", num_results=1
    )
    assert result == "https://apps.apple.com/us/developer/nintendo-co-ltd/id123456789"

def test_run_no_url_found(mock_google_search):
    mock_google_search.return_value = ["https://example.com", "https://another-site.com"]

    tool = DeveloperURLFinderTool()
    result = tool._run(developer_name="NonExistent Developer")

    assert result == "N/A: No App Store Developer Page URL found for this developer."

def test_run_error_handling(mock_google_search):
    mock_google_search.side_effect = Exception("Network issue")

    tool = DeveloperURLFinderTool()
    result = tool._run(developer_name="Nintendo Co., Ltd.")

    assert "Error finding developer page URL: Network issue" in result
