# tests/test_custom_tool.py

import pytest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup
import csv

# TODO: Fix this import
from src.appstore_data_agent.tools.custom_tool import (
    GameAppInfoScraperTool,
    APP_STORE_URL,
    OUTPUT_CSV_FILE,
    SCRAPED_FREE_GAMES_FILE,
    SCRAPED_PAID_GAMES_FILE,
    scrape_game_details,
    is_game_free2play,
    write_to_csv,
)

# Mock HTML content
MOCK_GAME_DETAIL_HTML = """
<h1 class="product-header__title">Test Game Name</h1>
<h2 class="product-header__identity app-header__identity"><a href="https://apps.apple.com/us/developer/test-developer/id123456789">Test Developer</a></h2>
<span class="we-customer-ratings__averages__display">4.5</span>
<section class="l-content-width section section--bordered section--information">
    <dl class="information-list information-list--app medium-columns l-row">
        <div class="information-list__item l-column small-12 medium-6 large-4 small-valign-top">Size400 MB</div>
        <div class="information-list__item l-column small-12 medium-6 large-4 small-valign-top">Age Rating4+</div>
        <div class="information-list__item l-column small-12 medium-6 large-4 small-valign-top">PriceFree</div>
        <div class="information-list__item l-column small-12 medium-6 large-4 small-valign-top">
            <span class="information-list__item__definition">Action</span>
        </div>
    </dl>
</section>
<div class="supports-list__item__copy">Supports Game Center, Achievements, Leaderboards</div>
"""

MOCK_DEVELOPER_PAGE_HTML = """
<section class="l-content-width section section--bordered">
    <a href="https://apps.apple.com/us/app/test-game-0/id000000000">Game 0</a>
    <a href="https://apps.apple.com/us/app/test-game-1/id111111111">Game 1</a>
    <a href="https://apps.apple.com/us/app/test-game-2/id222222222">Game 2</a>
</section>
"""

MOCK_APP_STORE_STORY_HTML = """
<a class="link link--no-tint link--no-decoration we-product-collection__item" href="https://apps.apple.com/us/app/featured-game-1/id333333333"></a>
<a class="link link--no-tint link--no-decoration we-product-collection__item" href="https://apps.apple.com/us/app/featured-game-2/id444444444"></a>
"""

@pytest.fixture
def mock_response():
    with patch("requests.get") as mock_get:
        yield mock_get

@pytest.fixture
def mock_write_to_csv():
    with patch("src.appstore_data_agent.tools.custom_tool.write_to_csv") as mock_write:
        yield mock_write

# Test cases for scrape_game_details
def test_scrape_game_details_success(mock_response):
    mock_response.return_value.text = MOCK_GAME_DETAIL_HTML
    mock_response.return_value.raise_for_status.return_value = None
    
    game_url = "https://apps.apple.com/us/app/test-game/id12345"
    details, developer_url = scrape_game_details(game_url)

    assert details["Game Name"] == "Test Game Name"
    assert details["Developer Name"] == "Test Developer"
    assert details["Ratings"] == "4.5"
    assert details["Size"] == "400 MB"
    assert details["Age Limit"] == "4+"
    assert details["Price"] == "Free"
    assert details["Genre"] == "Action"
    assert details["Game Center Integ"] == "Yes"
    assert details["Achievement"] == "Yes"
    assert details["Leaderboard"] == "Yes"
    assert developer_url == "https://apps.apple.com/us/developer/test-developer/id123456789"

def test_scrape_game_details_network_error(mock_response):
    mock_response.side_effect = requests.exceptions.RequestException("Network error")
    game_url = "https://apps.apple.com/us/app/test-game/id12345"
    details, developer_url = scrape_game_details(game_url)
    assert details == {
        "Developer Name": "N/A",
        "Game Name": "N/A",
        "Ratings": "N/A",
        "Size": "0 MB",
        "Age Limit": "N/A",
        "Price": "Free",
        "Genre": "N/A",
        "Achievement": "No",
        "Leaderboard": "No",
        "Game Center Integ": "No",
    }
    assert developer_url is None

# Test cases for is_game_free2play
def test_is_game_free2play_free_game():
    game_details = {"Price": "Free"}
    assert is_game_free2play(game_details) is True

def test_is_game_free2play_paid_game():
    game_details = {"Price": "$4.99"}
    assert is_game_free2play(game_details) is False

# Test cases for write_to_csv (mocking open)
@patch("builtins.open", new_callable=MagicMock)
def test_write_to_csv(mock_open):
    games_data = [
        {"Developer Name": "Dev1", "Game Name": "Game1", "Ratings": "5.0", "Size": "100 MB", "Age Limit": "4+", "Price": "Free", "Genre": "Action", "Game Center Integ": "Yes", "Achievement": "Yes", "Leaderboard": "Yes"},
        {"Developer Name": "Dev2", "Game Name": "Game2", "Ratings": "4.0", "Size": "200 MB", "Age Limit": "9+", "Price": "$2.99", "Genre": "Puzzle", "Game Center Integ": "No", "Achievement": "No", "Leaderboard": "No"},
    ]
    csv_file_name = "test_output.csv"
    # TODO: Fix this test
    # write_to_csv(csv_file_name, games_data)

    # mock_open.assert_called_once_with(csv_file_name, 'w', newline='', encoding='utf-8')
    # mock_csvfile = mock_open()
    # mock_csvfile.write.assert_any_call("Developer Name,Game Name,Ratings,Size,Age Limit,Price,Genre,Game Center Integ,Achievement,Leaderboard\r\n")
    # mock_csvfile.write.assert_any_call("Dev1,Game1,5.0,100 MB,4+,Free,Action,Yes,Yes,Yes\r\n")
    # mock_csvfile.write.assert_any_call("Dev2,Game2,4.0,200 MB,9+,$2.99,Puzzle,No,No,No\r\n")

# Test cases for GameAppInfoScraperTool._run
def test_run_with_seed_url_and_matching_developer(mock_response, mock_write_to_csv):
    mock_response.side_effect = [
        MagicMock(text=MOCK_DEVELOPER_PAGE_HTML, raise_for_status=MagicMock()), # Developer page
        MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()), # Game 0 details
        MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()), # Game 1 details
        MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()), # Game 2 details
    ]

    tool = GameAppInfoScraperTool()
    result = tool._run(
        app_developer="Test Developer",
        seed_developer_url="https://apps.apple.com/us/developer/test-developer/id123456789"
    )

    assert "Scraping complete" in result
    assert mock_write_to_csv.call_count == 1  # For OUTPUT_CSV_FILE, FREE


# def test_run_with_only_seed_url_derives_developer(mock_response, mock_write_to_csv):
#     mock_response.side_effect = [
#         MagicMock(text=MOCK_DEVELOPER_PAGE_HTML, raise_for_status=MagicMock()),  # Developer page
#         MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()), # Game 0 details
#         MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()),  # Game 1 details
#         MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()),  # Game 2 details
#     ]

#     tool = GameAppInfoScraperTool()
#     result = tool._run(
#         app_developer="", # No developer specified, should be derived from seed URL
#         seed_developer_url="https://apps.apple.com/us/developer/test-developer/id123456789"
#     )

#     assert "Scraping complete" in result
#     assert mock_write_to_csv.call_count == 2 # For OUTPUT_CSV_FILE, FREE

def test_run_no_seed_url_scrapes_app_store_url(mock_response, mock_write_to_csv):
    mock_response.side_effect = [
        MagicMock(text=MOCK_APP_STORE_STORY_HTML, raise_for_status=MagicMock()),  # Main App Store story
        MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()),  # Featured Game 1 details
        MagicMock(text=MOCK_GAME_DETAIL_HTML, raise_for_status=MagicMock()),  # Featured Game 2 details
    ]

    tool = GameAppInfoScraperTool()
    result = tool._run(
        app_developer="Test Developer", # Must provide developer to filter in absence of seed URL
        seed_developer_url=""
    )

    assert "Scraping complete" in result
    assert mock_write_to_csv.call_count == 1 # For OUTPUT_CSV_FILE, FREE

def test_run_network_error_during_main_scrape(mock_response, mock_write_to_csv, capsys):
    mock_response.side_effect = requests.exceptions.RequestException("Network error during main scrape")

    tool = GameAppInfoScraperTool()
    result = tool._run(
        app_developer="Test Developer",
        seed_developer_url=""
    )

    assert "Scraping error" in result # The message is generic even on error
    assert "Error fetching the main App Store page" in capsys.readouterr().out # Check print output
    mock_write_to_csv.assert_not_called()

def test_run_no_game_data_found(mock_response, mock_write_to_csv):
    mock_response.side_effect = [
        MagicMock(text="<html><body>No content</body></html>", raise_for_status=MagicMock()),  # Developer page no links
        MagicMock(text="<html><body>No content</body></html>", raise_for_status=MagicMock()),  # App Store no links
    ]

    tool = GameAppInfoScraperTool()
    result = tool._run(
        app_developer="Test Developer",
        seed_developer_url="https://apps.apple.com/us/developer/test-developer/id123456789"
    )

    assert "Scraping complete. No data to write." in result
    assert mock_write_to_csv.call_count == 0  # For OUTPUT_CSV_FILE, FREE
    mock_write_to_csv.assert_not_called()
