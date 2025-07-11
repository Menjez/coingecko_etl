import requests
from bs4 import BeautifulSoup
import csv

def scrape_injury_data():
    payload = {
        'api_key': '4d5beac65e4f04562a0826c3ac4bc6d1',
        'url': 'https://www.premierinjuries.com/injury-table.php',
        'render': 'true'  # important for JS-heavy Cloudflare pages
    }

    response = requests.get('https://api.scraperapi.com/', params=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def extract_club_data():
    with open("E0.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)
        print(f"Headers: {headers}")



