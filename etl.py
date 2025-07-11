import extract
import transform
import load

API_KEY = 'your_api_key'
URL = 'https://www.premierinjuries.com/injury-table.php'

def run_etl():
    html_content = extract.scrape_injury_data()
    data = transform.transform_injury_data(html_content)
    load.bulk_insert(data)
    


run_etl()