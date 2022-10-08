# IMPORTS
import sqlite3
import os

# Constants
MAINFOLDER = os.curdir
DATAFOLDER = os.path.join(MAINFOLDER, 'scraping', 'data')
DATABASEFOLDER = os.path.join(os.curdir, 'database')

con = sqlite3.connect(os.path.join(DATABASEFOLDER, 'peru.db'))
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS competition')
cur.execute('CREATE TABLE competition(id integer primary key, name, year)')

competition_data = []
for year in os.listdir(DATAFOLDER):
    YEARFOLDER = os.path.join(DATAFOLDER, year)
    for competition in os.listdir(YEARFOLDER):
        competition_data.append((None, competition, year))

cur.executemany("INSERT INTO competition VALUES(?, ?, ?)", competition_data)
con.commit()
