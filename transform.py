from bs4 import BeautifulSoup

def transform_injury_data(html):
    if not html:
        print("No html")
        return {}

    table = html.find('table', class_='injury-table injury-table-full')
    if not table:
        print("Injury table not found.")
        return {}

    rows = table.find_all('tr')
    
    print("done")
    return clean_and_extract(rows)

def clean_and_extract(rows):
    teams_injuries = {}
    current_team = None

    for row in rows:
        class_list = row.get("class", [])

        if "heading" in class_list:
            current_team = extract_team_name(row)
            if current_team:
                teams_injuries[current_team] = []
            continue

        if should_skip_row(class_list):
            continue

        if "player-row" in class_list:
            injury_data = extract_player_injury(row)
            if injury_data and current_team:
                teams_injuries[current_team].append(injury_data)

    return teams_injuries


def extract_team_name(row):
    div = row.find("div", class_="injury-team")
    return div.get_text(strip=True) if div else None


def should_skip_row(class_list):
    if not class_list:
        return True
    skip_keywords = ['sub-head', 'team-ad-slot']
    return any(cls in skip_keywords for cls in class_list) or any("showTeam" in cls for cls in class_list)


def extract_player_injury(row):
    cells = row.find_all("td")
    if len(cells) < 6:
        return None  # Guard in case layout is incomplete

    def strip_prefix(text, prefix):
        if text.startswith(prefix) and len(text) > len(prefix):
            return text[len(prefix):].strip()
        return text

    # Clean each cell and remove field prefixes
    player = strip_prefix(clean_text(cells[0].get_text()), "Player")
    reason = strip_prefix(clean_text(cells[1].get_text()), "Reason")
    detail = strip_prefix(clean_text(cells[2].get_text()), "Further Detail")
    return_date = strip_prefix(clean_text(cells[3].get_text()), "Potential Return")
    condition = strip_prefix(clean_text(cells[4].get_text()), "Condition")
    status = strip_prefix(clean_text(cells[5].get_text()), "Status")

    return {
        "Player": player,
        "Reason": reason,
        "Further Detail": detail,
        "Potential Return": return_date,
        "Condition": condition,
        "Status": status
    }

def clean_text(text):
    return ' '.join(text.strip().split()) if text else ''
