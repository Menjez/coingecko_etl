import psycopg2 as pg
from datetime import date

DB_NAME = "database_name"
DB_USER = "username"
DB_PASSWORD = "password"
DB_HOST = "hostname"
DB_PORT = "port_number"

#Establish connection with db
conn = pg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

#Create schema
cur.execute("""
    CREATE SCHEMA IF NOT EXISTS prem_injury
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS prem_injury.teams(
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE
    );
""")
   
cur.execute(f"""
    CREATE TABLE IF NOT EXISTS prem_injury.players (
        id SERIAL PRIMARY KEY,
        name TEXT,
        team_id INTEGER REFERENCES prem_injury.teams(id),
        UNIQUE(name, team_id)
    )
""")
   

cur.execute(f"""
    CREATE TABLE IF NOT EXISTS prem_injury.injuries (
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES prem_injury.players(id),
        reason TEXT,
        further_detail TEXT,
        potential_return TEXT,
        condition TEXT,
        status TEXT,
        reported_at DATE DEFAULT CURRENT_DATE
)
""")


def insert_injury(data):
    team_name = data["team"]
    player_name = data["player"]
    injury = data["injury"]

    # Get or insert team
    cur.execute(f"""
        SELECT id FROM prem_injury.teams WHERE name = %s
    """, (team_name,))
    result = cur.fetchone()
    if result:
        team_id = result[0]
    else:
        cur.execute(f"""
            INSERT INTO prem_injury.teams (name) VALUES (%s) RETURNING id
        """, (team_name,))
        team_id = cur.fetchone()[0]

    # Get or insert player
    cur.execute(f"""
        SELECT id FROM prem_injury.players WHERE name = %s AND team_id = %s
    """, (player_name, team_id))
    result = cur.fetchone()
    if result:
        player_id = result[0]
    else:
        cur.execute(f"""
            INSERT INTO prem_injury.players (name, team_id)
            VALUES (%s, %s) RETURNING id
        """, (player_name, team_id))
        player_id = cur.fetchone()[0]

    # Insert injury (always inserted)
    cur.execute(f"""
        INSERT INTO prem_injury.injuries (
            player_id, reason, further_detail,
            potential_return, condition, status, reported_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        player_id,
        injury.get("Reason", ""),
        injury.get("Further Detail", ""),
        injury.get("Potential Return", ""),
        injury.get("Condition", ""),
        injury.get("Status", ""),
        date.today()
    ))

    print(f"Inserted injury for {player_name} ({team_name})")


def bulk_insert(transformed_data):
    for team_name, injury_list in transformed_data.items():
        for player_data in injury_list:
            insert_injury({
                "team": team_name,
                "player": player_data["Player"],
                "injury": {
                    "Reason": player_data.get("Reason", ""),
                    "Further Detail": player_data.get("Further Detail", ""),
                    "Potential Return": player_data.get("Potential Return", ""),
                    "Condition": player_data.get("Condition", ""),
                    "Status": player_data.get("Status", "")
                }
            })
    conn.commit()
    print("all injuries committed to db")