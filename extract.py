import requests
from bs4 import BeautifulSoup
import csv

def scrape_injury_data():
    payload = {
        'api_key': 'your_api_key',
        'url': 'https://www.premierinjuries.com/injury-table.php',
        'render': 'true' 
    }

    response = requests.get('https://api.scraperapi.com/', params=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def extract_club_data():
    with open("E0.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)
        print(f"Headers: {headers}")



