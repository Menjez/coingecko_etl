import requests
from bs4 import BeautifulSoup

def scrape_with_scraperapi():
    payload = {
        'api_key': '4d5beac65e4f04562a0826c3ac4bc6d1',
        'url': 'https://www.premierinjuries.com/injury-table.php',
        'render': 'true'  # important for JS-heavy Cloudflare pages
    }

    response = requests.get('https://api.scraperapi.com/', params=payload)
    soup = BeautifulSoup(response.text, 'html.parser')

    print(soup)

scrape_with_scraperapi()
