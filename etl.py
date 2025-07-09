import transform

API_KEY = '4d5beac65e4f04562a0826c3ac4bc6d1'
URL = 'https://www.premierinjuries.com/injury-table.php'

def run_etl():
    with open("injury_html.txt", "r", encoding="utf-8") as file:
        html_content = file.read()

    data = transform.transform_injury_data(html_content)
    for team, injuries in data.items():
        print(f"{team} ({len(injuries)} injuries):")
        for injury in injuries:
            print("  -", injury)


run_etl()