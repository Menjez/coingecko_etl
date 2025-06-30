from bs4 import BeautifulSoup
import requests

API_KEY = '3a2bf5a9ec452b4dfbd89e7f44e22bb2'

##scrapperAPI to bypass robot verification, render for JS content

def scrapper():
    payload = {
        'api_key': API_KEY ,
        'url': 'https://www.premierinjuries.com/injury-table.php' ,
        'render': 'true'
    }

    raw_html = requests.get('https://api.scraperapi.com', params=payload)
    soup = BeautifulSoup(raw_html.text, 'html.parser')
    injury_table = soup.find('table', class_='injury-table injury-table-full')

    if not injury_table:
        print("Table not found")
        return {}
    
    teams_injuries = {}
    current_team = None

    rows = injury_table.find_all('tr')

    for row in rows:
        class_list = row.get('class', [])
        
        # Check if this is a team heading row
        if 'heading' in class_list:
            # Extract team name from the row
            team_cell = row.find('div', class_='injury-team')
            if team_cell:
                current_team = team_cell.get_text(strip=True)
                teams_injuries[current_team] = []
                continue
        
        # Skip sub-headers and ad slots
        if any(cls in class_list for cls in ['sub-head', 'team-ad-slot']):
            continue
            
        # Skip rows that contain team separators
        if any('showTeam' in cls for cls in class_list):
            continue
            
        cells = row.find_all('td')

         # Only process rows with player data (should have 6+ cells)
        if len(cells) >= 6 and current_team:
            player = cells[0].get_text(strip=True)
            reason = cells[1].get_text(strip=True)
            further_detail = cells[2].get_text(strip=True)
            return_date = cells[3].get_text(strip=True)
            condition = cells[4].get_text(strip=True)
            status = cells[5].get_text(strip=True)
            
            # Skip empty rows
            if player:
                injury_data = {
                    "Player": player,
                    "Reason": reason,
                    "Further Detail": further_detail,
                    "Potential Return": return_date,
                    "Condition": condition,
                    "Status": status
                }
                teams_injuries[current_team].append(injury_data)
    
    return teams_injuries


def print_injuries_by_team():
    """Print injuries grouped by team in a readable format"""
    injuries_data = scrapper()
    
    for team, injuries in injuries_data.items():
        print(f"\n{'='*50}")
        print(f"TEAM: {team}")
        print(f"{'='*50}")
        print(f"Total Injuries: {len(injuries)}")
        
        if injuries:
            for i, injury in enumerate(injuries, 1):
                print(f"\n{i}. {injury['Player']}")
                print(f"   Reason: {injury['Reason']}")
                print(f"   Details: {injury['Further Detail']}")
                print(f"   Return: {injury['Potential Return']}")
                print(f"   Condition: {injury['Condition']}")
                print(f"   Status: {injury['Status']}")
        else:
            print("No injuries reported")


print_injuries_by_team()