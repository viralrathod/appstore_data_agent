import requests
from bs4 import BeautifulSoup
import csv
from crewai.tools import BaseTool, FileWriterTool
from typing import Type
from pydantic import BaseModel, Field

# Base URL for the App Store's top free games story
APP_STORE_URL = "https://apps.apple.com/us/story/id1302444839"

# CSV file name
OUTPUT_CSV_FILE = "game_center_games.csv"
SCRAPED_FREE_GAMES_FILE = "game_center_f2p_games.csv"
SCRAPED_PAID_GAMES_FILE = "game_center_paid_games.csv"

def scrape_game_details(game_url):
    game_details = {
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
    developer_url = None
    try:
        response = requests.get(game_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Game Name
        game_name_tag = soup.find('h1', class_='product-header__title')
        if game_name_tag:
            game_details["Game Name"] = game_name_tag.get_text(strip=True)

        print("Processing game: " +game_name_tag.get_text(strip=True))
        
        # Developer Name
        developer_tag = soup.find('h2', class_='product-header__identity app-header__identity')
        if developer_tag and developer_tag.find('a'):
            game_details["Developer Name"] = developer_tag.find('a').get_text(strip=True)
            developer_url = developer_tag.find('a').get('href')
            print(f"Developer URL: {developer_url}")

        # Ratings
        ratings_tag = soup.find('span', class_='we-customer-ratings__averages__display')
        if ratings_tag:
            game_details["Ratings"] = ratings_tag.get_text(strip=True)

        # Info section begins
        info_divs = soup.find('section', class_='l-content-width section section--bordered section--information').find('dl', class_='information-list information-list--app medium-columns l-row').find_all('div', class_='information-list__item l-column small-12 medium-6 large-4 small-valign-top')

        for div_item in info_divs:
            if "Size" in div_item.getText(strip=True):
                size_val = div_item.getText(strip=True)
                size_val = size_val[4:]
                game_details["Size"] = size_val
            if "Age Rating" in div_item.getText(strip=True):
                age_rating_val = div_item.getText(strip=True)
                age_rating_val = age_rating_val[10:12]
                game_details["Age Limit"] = age_rating_val
            if "Price" in div_item.getText(strip=True):
                price_val = div_item.getText(strip=True)
                price_val = price_val[5:]
                game_details["Price"] = price_val
        # Genre
        genre_tag = soup.find('span', class_='information-list__item__definition')
        if genre_tag:
            game_details["Genre"] = genre_tag.get_text(strip=True)

        # Game Center functionality (Achievement, Leaderboard)
        supports_section = soup.find('div', class_='supports-list__item__copy')
        if supports_section:
            support_text = supports_section.get_text().lower()
            if "Game Center" in support_text or "leaderboards" in support_text or "achievements" in support_text:
                game_details["Game Center Integ"] = "Yes"
            if "achievements" in support_text:
                game_details["Achievement"] = "Yes"
            if "leaderboards" in support_text:
                game_details["Leaderboard"] = "Yes"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching game details for {game_url}: {e}")
    return game_details, developer_url

def is_game_free2play(game_details):
    if "Free" in game_details["Price"]:
        return True
    else:
        return False

def write_to_csv(csv_file_name, games_data):
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Developer Name", "Game Name", "Ratings", "Size", "Age Limit", "Price", "Genre", "Game Center Integ", "Achievement", "Leaderboard"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(games_data)


class GameAppInfoScraperToolInput(BaseModel):
    """Input schema for GameAppInfoScraperToolInput."""
    app_developer: str = Field(..., description="Description of the argument")
    seed_game_url: str = Field(..., description="Description of the argument")

class GameAppInfoScraperTool(BaseTool):
    name: str = "Games App Info Scraper for App Store"
    description: str = (
        "Use this tool to scrape the information of a game apps in the App Store."
    )
    args_schema: Type[BaseModel] = GameAppInfoScraperToolInput

    def _run(self, app_developer: str, seed_game_url: str) -> str:
        game_urls = []
        app_developer_filter = None

        if app_developer:
            app_developer_filter = app_developer
            print(f"Filtering by app developer: {app_developer_filter}")

        if seed_game_url:
            game_urls.append(seed_game_url)
            print(f"Starting with seed game URL: {seed_game_url}")

            seed_game_details, seed_developer_url = scrape_game_details(seed_game_url)
            if not seed_game_details:
                return "Error: Could not retrieve details for the seed game URL."

            seed_developer_name = seed_game_details["Developer Name"]
            if app_developer_filter and seed_developer_name != app_developer_filter:
                return f"Error: Seed game developer '{seed_developer_name}' does not match specified app developer '{app_developer_filter}'."
            
            if not app_developer_filter:
                app_developer_filter = seed_developer_name
                print(f"No app developer specified. Using developer from seed game: {seed_developer_name}")

            if seed_developer_url:
                developer_store_url = seed_developer_url
                print(f"Attempting to scrape developer page: {developer_store_url}")
                try:
                    dev_response = requests.get(developer_store_url)
                    dev_response.raise_for_status()
                    dev_soup = BeautifulSoup(dev_response.text, 'html.parser')
                    
                    dev_game_links_section = dev_soup.find('section', class_='l-content-width section section--bordered')
                    if dev_game_links_section:
                        dev_game_links = dev_game_links_section.find_all('a')

                        total_dev_links = len(dev_game_links)
                        print(f"Total Games found on {developer_store_url} Dev page is {total_dev_links}")
                        for link in dev_game_links:
                            print(f"Collecting link: {link}")
                            if link.get('href') and "/app/" in link.get('href'):
                                game_urls.append(link.get('href'))
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching developer page {developer_store_url}: {e}")
        
        if not app_developer_filter:
            return "Error: No app developer specified via app_developer or derived from seed_game_url."

        if not seed_game_url or not game_urls: 
            print("App Developer URL did not seem to work... Here's a sample report for Top Free and Paid Games")
            try:
                response = requests.get(APP_STORE_URL)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                game_links = soup.find_all('a', class_='link link--no-tint link--no-decoration we-product-collection__item')
                for link in game_links:
                    if link.get('href') and "/app/" in link.get('href'):
                        game_urls.append(link.get('href'))
            except requests.exceptions.RequestException as e:
                print(f"Error fetching the main App Store page: {e}")

        game_urls = list(set(game_urls))
        scraped_games_data = []
        top_free_games_data = []
        top_paid_games_data = []

        print(f"Found {len(game_urls)} game URLs.")
        
        for url in game_urls:
            details, _ = scrape_game_details(url)
            if details:
                scraped_games_data.append(details)
                if is_game_free2play(details):
                    top_free_games_data.append(details)
                else:
                    top_paid_games_data.append(details)

        # Write to CSV
        if scraped_games_data and len(scraped_games_data) > 0:
            write_to_csv(OUTPUT_CSV_FILE, scraped_games_data)
            print(f"Successfully wrote {len(scraped_games_data)} games to {OUTPUT_CSV_FILE}")
        else:
            print("No game data to write to main CSV.")

        if top_free_games_data and len(top_free_games_data) > 0:
            write_to_csv(SCRAPED_FREE_GAMES_FILE, top_free_games_data)
            print(f"Successfully wrote {len(top_free_games_data)} games to {SCRAPED_FREE_GAMES_FILE}")
        else:
            print("No free game data to write.")

        if top_paid_games_data and len(top_paid_games_data) > 0:
            write_to_csv(SCRAPED_PAID_GAMES_FILE, top_paid_games_data)
            print(f"Successfully wrote {len(top_paid_games_data)} games to {SCRAPED_PAID_GAMES_FILE}")
        else:
            print("No paid game data to write.")

        return f"Scraping complete. Data written to {OUTPUT_CSV_FILE}, {SCRAPED_FREE_GAMES_FILE}, and {SCRAPED_PAID_GAMES_FILE}."
