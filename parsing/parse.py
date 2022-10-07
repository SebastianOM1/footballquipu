from bs4 import BeautifulSoup
import pprint
from numpy import insert

import requests

def clean_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('tbody')
    rows = table.find_all('td')

    clean_rows = [row.text for row in rows if row.text != '' and row.text != ' ']
    return clean_rows

def parse(rows):
    """ Information to collect
    Arena (DONE)
    City (DONE)
    Date (DONE)
    Time (DONE)
   
    Referee (DONE)
    Assistant referee 1 (DONE)
    Assistant referee 2 (DONE)
    Auxiliary (DONE)
   
    Team 0 and formation (DONE)
    Team 1 and formation (DONE)
   
    Score (DONE)
    Player info (DONE)

    Sub info
    Manager info (DONE)

    Substitutions (DONE)
    Goals (DONE)
    """
   
    dic = dict()
    try:
        dic['Stadium'] = rows[rows.index('EST') + 1]
    except:
        dic['Stadium'] = rows[2]
    dic['City'] = rows[rows.index('CIU') + 1]
    dic['Date'] = rows[rows.index('FEC') + 1]
    dic['Time'] = rows[rows.index('HOR') + 1]

    dic['Referee'] = rows[rows.index('ÁRB') + 1]
    dic['Assistant referee 1'] = rows[rows.index('AA1') + 1]
    dic['Assistant referee 2'] = rows[rows.index('AA2') + 1]
    try:
        dic['Auxiliary'] = rows[rows.index('AUX') + 1]
    except:
        rows[rows.index('AA2') + 4] = 'AUX'
        dic['Auxiliary'] = rows[rows.index('AUX') + 1]
        
    i = rows.index('AUX') + 2
    split_team_formation_1 = rows[i].split(' ')
    split_team_formation_2 = rows[i + 1].split(' ')
    dic['Team 1'], dic['Team 1 Formation'] = ' '.join(split_team_formation_1[:-1]), split_team_formation_1[-1]
    dic['Team 2'], dic['Team 2 Formation'] = ' '.join(split_team_formation_2[:-1]), split_team_formation_2[-1]
   
    dic['Score team 1'] = rows[3]
    dic['Score team 2'] = rows[5]    

    ### Get substitutions and goals
    substitutions = []
    i = rows.index('MIN')
    i += rows[i:i+6].count('MIN') + rows.count('Entra') + rows.count('Sale')
    while rows[i] != 'MIN' and rows[i] != 'Capitán' and rows[i] != 'Incidencias' and rows[i] != 'Anotador':
        inputs = [rows[i], rows[i + 1], rows[i + 2]]
        if any([True if elem == '-' else False for elem in inputs]):
            i += inputs.count('-')
        else:
            minute = int(rows[i].replace('+', '').replace("'", ''))
            in_player = rows[i + 1]
            out_player = rows[i + 2]
            substitutions.append([minute, in_player, out_player])
            i += 3
    dic['Substitutions'] = substitutions
    
    ### CHECK PRESENCE OF MIN ###
    insert_indexes = []
    for anotador_index in [index for index, s in enumerate(rows) if s == 'Anotador']:
        if rows[anotador_index - 1] != 'MIN':
            insert_indexes.append(anotador_index)
    for index in insert_indexes:
        rows.insert(index, 'MIN')

    if rows.count('MIN') > 4:
        if rows.count('MIN') == 6:
            goals = []
            i += 8
            while rows[i] != 'Capitán' and rows[i] != 'Definición de penales' and rows[i] != 'Incidencias' and rows[i] != 'MIN' and rows[i] != 'Definición por penales':
                inputs = [rows[i], rows[i + 1], rows[i + 2], rows[i + 3]]
                if all([True if elem == '-' or elem == 'Capitán' or elem == 'La figura' else False for elem in inputs]) > 1:
                    i += 4
                else:
                    minute = int(rows[i].replace('+', '').replace("'", ''))
                    scorer = rows[i + 1]
                    with_part = rows[i + 2]
                    goal_type = rows[i + 3]
                    if with_part == 'Capitán' and goal_type == 'La figura':
                        with_part = ''
                        goal_type = ''
                        i += 2
                    elif with_part == 'Capitán' or with_part.isnumeric():
                        with_part = goal_type
                        goal_type = ''
                        goals.append([minute, scorer, with_part, goal_type])
                        i += 3
                    elif goal_type == 'Capitán' or goal_type.isnumeric():
                        goal_type = with_part
                        with_part = ''
                        goals.append([minute, scorer, with_part, goal_type])
                        i += 3
                    else:
                        goals.append([minute, scorer, with_part, goal_type])
                        i += 4
            dic['Goals'] = goals
        else:
            i = [index for index, s in enumerate(rows) if s == 'Anotador'][1] + 3
            goals = []
            while rows[i] != 'Capitán' and rows[i] != 'Definición de penales' and rows[i] != 'Incidencias':
                minute = int(rows[i].replace('+', ''))
                scorer = rows[i + 1]
                with_part = rows[i + 2]
                goal_type = rows[i + 3]
                goals.append([minute, scorer, with_part, goal_type])
                i += 4
            dic['Goals'] = goals
    else:
        dic['Goals'] = []

    ### Managers
    i = rows.index('DT') + 1
    dic['Team 1 Manager'] = rows[i]
    dic['Team 2 Manager'] = rows[i + 2]
   
    ### Figure out where list of players begins (After 2 instances of '# Jugadores 1A 2A TR Nota)
    try:
        start_of_players = [index for index, s in enumerate(rows) if s == 'Nota'][1] + 1
    except:
        start_of_players = rows.index('AUX') + 4

    ### Figure out where list of players ends (At 'Capitan')
    end_of_players = rows.index('DT')

    player_data = rows[start_of_players:end_of_players]
    ### Each player has his shirt number before himself, figure out other numbers
    ## List for player goes like [Shirt Number, First Yellow, Second Yellow, Red, Score)
    dic['Starting eleven 1'], dic['Starting eleven 2'] = get_players(player_data, True)
    
    last_starter_name = dic['Starting eleven 2'][-1][0]
    last_starter_name_index = player_data.index(last_starter_name)
    first_sub = last_starter_name_index + numbers_in_front(player_data, last_starter_name_index)
    subs_data = player_data[first_sub:end_of_players]
    dic['Subs 1'], dic['Subs 2'] = get_players(subs_data, False)
    return dic

def numbers_in_front(arr, i):
    total = 0
    for index in range(i+1, len(arr)):
        if any([c.isnumeric() for c in arr[index]]) or arr[index].strip() == '-' or arr[index].strip() == '+':
            total += 1
        else:
            return total
    return total + 1

def find_no_shirt_number(arr):
    indexes = []
    isname = lambda x: True if not x.replace('+', '').replace("'", '').isnumeric() and x != '-' and x != '+' else False
    for i in range(len(arr) - 1):
        if isname(arr[i]) and isname(arr[i + 1]):
            indexes.append(i + 1)
    for i in range(len(indexes)):
        arr.insert(indexes[i] - i, '-1')
    return arr

def get_players(arr, starters):
    ### LIMITATION: Unable to detect straight red cards, processes them as yellow cards
    players_team_0 = []
    players_team_1 = []
    reading = 0
    current = 0
    
    arr = find_no_shirt_number(arr)
    while len(players_team_0) + len(players_team_1) < 22 if starters else current < len(arr) and arr[current] != 'DT':
        num_in_front = numbers_in_front(arr, current+1)
        end_of_data = current + 1 + numbers_in_front(arr, current+1) if num_in_front else 0
        player = [0, 0, 0, 0, 0]
        player_read = arr[current:end_of_data]
        for i,d in enumerate(player_read):
            if not d.isnumeric() and d != '-':
                name_index = i
        name = player_read.pop(name_index)
        player[0] = int(player_read[0].replace(',', ''))
        if starters:
            player[4] = int(player_read[len(player_read) - 1]) if player_read[len(player_read) - 1].isnumeric() else 0
        else:
            if len(player_read) > 1:
                player[4] = int(player_read[len(player_read) - 1]) if player_read[len(player_read) - 1].isnumeric() else 0
        if len(player_read) > 2:
            for i in range(1, len(player_read) - 1):
                if player_read[i].isnumeric():
                    player[i] = int(player_read[i])
                else:
                    player[i] = 0
        if reading == 0:
            players_team_0.append([name] + player)
        else:
            players_team_1.append([name] + player)
        current = end_of_data
        reading = (reading + 1) % 2
    
    return players_team_0, players_team_1

url = 'https://docs.google.com/spreadsheets/u/0/d/1MJbA_thRF9Rclo2lLvX-HE3HPdc_lSqnwIymYgbNt5U/pub?gid=0&range=A1:O43&output=html'
response = requests.get(url)
html = response.text
parse(clean_table(html))
