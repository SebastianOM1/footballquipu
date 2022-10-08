# IMPORTS
import sqlite3
import os
from parse import parse, clean_table

# Constants
MAINFOLDER = os.curdir
DATAFOLDER = os.path.join(MAINFOLDER, 'scraping', 'data')
DATABASEFOLDER = os.path.join(os.curdir, 'database')

con = sqlite3.connect(os.path.join(DATABASEFOLDER, 'peru.db'))
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS team')
cur.execute('CREATE TABLE team(id integer primary key, name, competition, FOREIGN KEY(competition) REFERENCES competition(id))')

team_data = []
for year in os.listdir(DATAFOLDER):
    YEARFOLDER = os.path.join(DATAFOLDER, year)
    for competition in os.listdir(YEARFOLDER):
        COMPETITIONFOLDER = os.path.join(YEARFOLDER, competition)
        query = "SELECT id FROM competition WHERE name='" + competition + "' and year ='" + year + "'"
        competition_id = cur.execute(query).fetchone()
        team_set = set()
        for file in os.listdir(COMPETITIONFOLDER):
            try:
                txt_file = open(os.path.join(COMPETITIONFOLDER, file), 'r')
                html = txt_file.read()
            except Exception as e:
                txt_file = open(os.path.join(COMPETITIONFOLDER, file), 'r', encoding='utf-8')
                html = txt_file.read()
            try:
                results = parse(clean_table(html))
                team_set.add(results['Team 1'])
                team_set.add(results['Team 2'])
            except Exception as e:
                    pass
        for team in team_set:
            team_data.append((None, team, competition_id[0]))
cur.executemany("INSERT INTO team VALUES(?, ?, ?)", team_data)
con.commit()
