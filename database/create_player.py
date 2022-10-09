# IMPORTS
import sqlite3
import os
from parse import parse, clean_table

# Constants
MAINFOLDER = os.curdir
DATAFOLDER = os.path.join(MAINFOLDER, 'scraping', 'data')
DATABASEFOLDER = os.path.join(os.curdir, 'database')

# Functions
# Player = [Name, Shirt Number, First Yellow, Second Yellow, Red, Score, Position]
def minutes_played(player, started, substitutions):
    name = player[0]
    red = player[4]
    if started:
        if red:
            return red
        out_players = [sub[2] for sub in substitutions]
        if name in out_players:
            return substitutions[out_players.index(name)][0]
        return 90
    else:
        in_players = [sub[1] for sub in substitutions]
        time_in = substitutions[in_players.index(name)][0]
        if red:
            return red - time_in
        out_players = [sub[2] for sub in substitutions]
        if name in out_players:
            return substitutions[out_players.index(name)][0] - time_in
        total_time = 90 - time_in
        return total_time if total_time > 0 else 0

yellow_cards = lambda player: [elem > 0 for elem in player[2:4]].count(True)
red_cards = lambda player: 1 if player[4] > 0 else 0

def goals_scored(player, goals):
    scorers = [goal[1] for goal in goals]
    name = player[0]
    num = 0
    for goal in goals:
        if goal[1] == name and goal[3].strip().lower() != 'autogol':
            num += 1
    return num

con = sqlite3.connect(os.path.join(DATABASEFOLDER, 'peru.db'))
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS player')
cur.execute('CREATE TABLE player(id integer primary key, team, name, shirt_number, position, games_started, games_sub, minutes_played, yellow_cards, red_cards, goals_scored, total_score, FOREIGN KEY(team) REFERENCES team(id))')

player_data = list()
for year in os.listdir(DATAFOLDER):
    YEARFOLDER = os.path.join(DATAFOLDER, year)
    for competition in os.listdir(YEARFOLDER):
        COMPETITIONFOLDER = os.path.join(YEARFOLDER, competition)
        player_dict = dict()
        for file in os.listdir(COMPETITIONFOLDER):
            try:
                txt_file = open(os.path.join(COMPETITIONFOLDER, file), 'r')
                html = txt_file.read()
            except Exception as e:
                txt_file = open(os.path.join(COMPETITIONFOLDER, file), 'r', encoding='utf-8')
                html = txt_file.read()
            try:
                results = parse(clean_table(html))
                team_1, team_2 = results['Team 1'], results['Team 2']
                team_1_query = "SELECT team.id FROM team JOIN competition WHERE team.name ='" + team_1 + "'"
                team_1_query += " and competition.name = '" + competition + "'"
                team_1_query += " and team.competition = competition.id and competition.year = '" + year + "'"
                team_1_id = cur.execute(team_1_query).fetchone()[0]
                team_2_query = "SELECT team.id FROM team JOIN competition WHERE team.name ='" + team_2 + "'"
                team_2_query += " and competition.name = '" + competition + "'"
                team_2_query += " and team.competition = competition.id and competition.year = '" + year + "'"
                team_2_id = cur.execute(team_2_query).fetchone()[0]
                starters_1, starters_2 = results['Starting eleven 1'], results['Starting eleven 2']
                subs_1, subs_2 = results['Subs 1'], results['Subs 2']
                substitutions = results['Substitutions']
                goals = results['Goals']

                for player in starters_1:
                    if (player[0], team_1_id) in player_dict:
                        player_dict[(player[0], team_1_id)][0] = player[1]
                        player_dict[(player[0], team_1_id)][1][player[-1]] += 1
                        player_dict[(player[0], team_1_id)][2] += 1
                        player_dict[(player[0], team_1_id)][4] += minutes_played(player, True, substitutions)
                        player_dict[(player[0], team_1_id)][5] += yellow_cards(player)
                        player_dict[(player[0], team_1_id)][6] += red_cards(player)
                        player_dict[(player[0], team_1_id)][7] += goals_scored(player, goals)
                        player_dict[(player[0], team_1_id)][8] += player[-2]
                    else:
                        position_dict = {'GK': 0, 'CB': 0, 'RB': 0, 'LB': 0, 'CMF': 0, 'RMF': 0, 'LMF': 0, 'AMF': 0, 'ST': 0}
                        position_dict[player[-1]] += 1
                        player_dict[(player[0], team_1_id)] = [
                            player[1],
                            position_dict,
                            1,
                            0,
                            minutes_played(player, True, substitutions),
                            yellow_cards(player),
                            red_cards(player),
                            goals_scored(player, goals),
                            player[-2]
                        ]

                for player in starters_2:
                    if (player[0], team_2_id) in player_dict:
                        player_dict[(player[0], team_2_id)][0] = player[1]
                        player_dict[(player[0], team_2_id)][1][player[-1]] += 1
                        player_dict[(player[0], team_2_id)][2] += 1
                        player_dict[(player[0], team_2_id)][4] += minutes_played(player, True, substitutions)
                        player_dict[(player[0], team_2_id)][5] += yellow_cards(player)
                        player_dict[(player[0], team_2_id)][6] += red_cards(player)
                        player_dict[(player[0], team_2_id)][7] += goals_scored(player, goals)
                        player_dict[(player[0], team_2_id)][8] += player[-2]
                    else:
                        position_dict = {'GK': 0, 'CB': 0, 'RB': 0, 'LB': 0, 'CMF': 0, 'RMF': 0, 'LMF': 0, 'AMF': 0, 'ST': 0}
                        position_dict[player[-1]] += 1
                        player_dict[(player[0], team_2_id)] = [
                            player[1],
                            position_dict,
                            1,
                            0,
                            minutes_played(player, True, substitutions),
                            yellow_cards(player),
                            red_cards(player),
                            goals_scored(player, goals),
                            player[-2]
                        ]
                        
                for player in subs_1:
                    if (player[0], team_1_id) in player_dict:
                        player_dict[(player[0], team_1_id)][0] = player[1]
                        player_dict[(player[0], team_1_id)][3] += 1
                        player_dict[(player[0], team_1_id)][4] += minutes_played(player, False, substitutions)
                        player_dict[(player[0], team_1_id)][5] += yellow_cards(player)
                        player_dict[(player[0], team_1_id)][6] += red_cards(player)
                        player_dict[(player[0], team_1_id)][7] += goals_scored(player, goals)
                    else:
                        position_dict = {'GK': 0, 'CB': 0, 'RB': 0, 'LB': 0, 'CMF': 0, 'RMF': 0, 'LMF': 0, 'AMF': 0, 'ST': 0}
                        player_dict[(player[0], team_1_id)] = [
                            player[1],
                            position_dict,
                            0,
                            1,
                            minutes_played(player, True, substitutions),
                            yellow_cards(player),
                            red_cards(player),
                            goals_scored(player, goals),
                            player[-2]
                        ]
                        
                for player in subs_2:
                    if (player[0], team_2_id) in player_dict:
                        player_dict[(player[0], team_2_id)][0] = player[1]
                        player_dict[(player[0], team_2_id)][3] += 1
                        player_dict[(player[0], team_2_id)][4] += minutes_played(player, False, substitutions)
                        player_dict[(player[0], team_2_id)][5] += yellow_cards(player)
                        player_dict[(player[0], team_2_id)][6] += red_cards(player)
                        player_dict[(player[0], team_2_id)][7] += goals_scored(player, goals)
                    else:
                        position_dict = {'GK': 0, 'CB': 0, 'RB': 0, 'LB': 0, 'CMF': 0, 'RMF': 0, 'LMF': 0, 'AMF': 0, 'ST': 0}
                        player_dict[(player[0], team_2_id)] = [
                            player[1],
                            position_dict,
                            0,
                            1,
                            minutes_played(player, True, substitutions),
                            yellow_cards(player),
                            red_cards(player),
                            goals_scored(player, goals),
                            player[-2]
                        ]
            except Exception as e:
                    pass
        for player in player_dict:
            name = player[0]
            team = player[1]
            shirt = player_dict[player][0]
            position = max(player_dict[player][1], key=player_dict[player][1].get)
            games_started = player_dict[player][2]
            games_sub = player_dict[player][3]
            min_played = player_dict[player][4]
            yellow_c = player_dict[player][5]
            red_c = player_dict[player][6]
            goals_s = player_dict[player][7]
            score = player_dict[player][8]
            player_data.append((None, team, name, shirt, position, games_started, games_sub, min_played, yellow_c, red_c, goals_s, score))
cur.executemany("INSERT INTO player VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", player_data)
con.commit()