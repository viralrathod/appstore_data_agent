import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field

class AppStoreScraperInput(BaseModel):
    """Input schema for AppStoreScraperTool."""
    url: str = Field(..., description="The App Store URL to scrape (developer page or game page).")

class AppStoreScraperTool(BaseTool):
    name: str = "App Store Scraper Tool"
    description: str = (
        "Scrapes an Apple App Store page (developer or game) and returns the HTML content or specific data."
    )
    args_schema: Type[BaseModel] = AppStoreScraperInput

    def _run(self, url: str) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # If it's a developer page, just return the game links to keep context manageable
            if "/developer/" in url:
                links = []
                # App Store developer pages typically list apps in sections
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if "/app/" in href and "/id" in href:
                        # Clean the URL
                        if "?" in href:
                            href = href.split("?")[0]
                        links.append(href)
                # Remove duplicates
                unique_links = list(set(links))
                return f"Developer Page Games Found: {', '.join(unique_links)}"
            
            # If it's a game page, return a summary of key elements for the LLM to parse
            else:
                data = {}
                # Extract relevant parts for LLM to process
                title = soup.find('h1', class_='product-header__title')
                data['title'] = title.get_text(strip=True) if title else "N/A"
                
                developer = soup.find('h2', class_='product-header__identity')
                data['developer'] = developer.get_text(strip=True) if developer else "N/A"
                
                rating = soup.find('span', class_='we-customer-ratings__averages__display')
                data['rating'] = rating.get_text(strip=True) if rating else "N/A"
                
                rating_count = soup.find('p', class_='we-customer-ratings__count')
                data['rating_count'] = rating_count.get_text(strip=True) if rating_count else "N/A"
                
                # Info list (Price, Size, Age Rating, etc)
                info_list = {}
                for div in soup.find_all('div', class_='information-list__item'):
                    dt = div.find('dt')
                    dd = div.find('dd')
                    if dt and dd:
                        info_list[dt.get_text(strip=True)] = dd.get_text(strip=True)
                data['info_list'] = info_list
                
                # Game Center
                supports = soup.find('div', class_='supports-list__item__copy')
                data['game_center'] = supports.get_text(strip=True) if supports else "None"
                
                return str(data)

        except Exception as e:
            return f"Error scraping URL {url}: {e}"

