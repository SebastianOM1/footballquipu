from xmlrpc.client import FastMarshaller
from bs4 import BeautifulSoup
import pprint
from numpy import insert

import requests

def clean_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('tbody')
    rows = table.find_all('td')

    clean_rows = [row.text for row in rows if row.text.strip() != '' and row.text.strip() != '-']
    return clean_rows

def parse(rows):
    dic = dict()
    try:
        dic['Stadium'] = rows[rows.index('EST') + 1]
    except:
        dic['Stadium'] = rows[2]
    dic['City'] = rows[rows.index('CIU') + 1].strip()
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
    dic['Team 1'], dic['Team 1 Formation'] = ' '.join(split_team_formation_1[:-1]), clean_formation(split_team_formation_1[-1])
    dic['Team 2'], dic['Team 2 Formation'] = ' '.join(split_team_formation_2[:-1]), clean_formation(split_team_formation_2[-1])
   
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
    get_positions(dic['Starting eleven 1'], dic['Team 1 Formation'])
    get_positions(dic['Starting eleven 2'], dic['Team 2 Formation'])
    
    last_starter_name = dic['Starting eleven 2'][-1][0]
    last_starter_name_index = player_data.index(last_starter_name)
    first_sub = last_starter_name_index + numbers_in_front(player_data, last_starter_name_index)
    subs_data = player_data[first_sub:end_of_players]
    dic['Subs 1'], dic['Subs 2'] = get_players(subs_data, False)
    return dic

def get_positions(team, formation):
    if type(formation) != str:
        return
    team[0].append('GK') # First is always goalie
    parts_of_formation = formation.split('-')
    mid_formation = parts_of_formation[1:-1]
    num_defenders = int(parts_of_formation[0])
    num_attackers = int(parts_of_formation[-1])
    assign_df(team[1: 1 + num_defenders], num_defenders)
    assign_mf(team[1 + num_defenders: -num_attackers], mid_formation)
    assign_fw(team[-num_attackers:], num_attackers)

def assign_df(players, num):
    if num == 3:
        for player in players:
            player.append('CB')
    elif num == 4:
        players[0].append('RB')
        players[1].append('CB')
        players[2].append('CB')
        players[3].append('LB')
    else: # num == 5
        players[0].append('RB')
        players[1].append('CB')
        players[2].append('CB')
        players[3].append('CB')
        players[4].append('LB')

def assign_mf(players, formation):
    if formation == ['2']:
        for player in players:
            player.append('CMF')
    elif formation == ['3']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('CMF')
    elif formation == ['4']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('RMF')
        players[3].append('LMF')
    elif formation == ['5']:
        players[0].append('RMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('CMF')
        players[4].append('LMF')
    elif formation == ['linea']:
        players[0].append('RMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('LMF')
    elif formation == ['cuadrado']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('AMF')
        players[3].append('AMF')
    elif formation == ['rombo']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('AMF')
    elif formation == ['trapecio']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('RMF')
        players[3].append('LMF')
    elif formation == ['4', '1']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('RMF')
        players[3].append('LMF')
        players[4].append('AMF')
    elif formation == ['2', '3']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('RMF')
        players[3].append('AMF')
        players[4].append('LMF')
    elif formation == ['cuadrado', '1']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('AMF')
        players[3].append('AMF')
        players[4].append('AMF')
    elif formation == ['3', '2']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('AMF')
        players[4].append('AMF')
    elif formation == ['4', '2']:
        player[0].append('RMF')
        player[1].append('CMF')
        player[2].append('CMF')
        player[3].append('LMF')
        player[4].append('AMF')
        player[5].append('AMF')
    elif formation == ['linea', '1']:
        player[0].append('RMF')
        player[1].append('CMF')
        player[2].append('CMF')
        player[3].append('LMF')
        player[4].append('AMF')
    elif formation == ['3', '1']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('AMF')
    elif formation == ['1', '4']:
        players[0].append('CMF')
        players[1].append('RMF')
        players[2].append('AMF')
        players[3].append('AMF')
        players[4].append('LMF')
    elif formation == ['1', '2']:
        players[0].append('CMF')
        players[1].append('AMF')
        players[2].append('AMF')
    elif formation == ['3', '3']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('RMF')
        players[4].append('AMF')
        players[5].append('LMF')
    elif formation == ['2', '4']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('RMF')
        players[3].append('AMF')
        players[4].append('AMF')
        players[5].append('LMF')
    elif formation == ['2', '1']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('AMF')
    elif formation == ['linea', '2']:
        players[0].append('RMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('LMF')
        players[4].append('AMF')
        players[5].append('AMF')
    elif formation == ['1', '3']:
        players[0].append('CMF')
        players[1].append('RMF')
        players[2].append('AMF')
        players[3].append('LMF')
    elif formation == ['2', '2']:
        players[0].append('CMF')
        players[1].append('CMF')
        players[2].append('AMF')
        players[3].append('AMF')
    elif formation == ['5', '1']:
        players[0].append('RMF')
        players[1].append('CMF')
        players[2].append('CMF')
        players[3].append('CMF')
        players[4].append('LMF')
        players[5].append('AMF')
    else:
        raise Exception('Unknown formation of shape: ', formation)
        
def assign_fw(players, num):
    if num < 3:
        for player in players:
            player.append('ST')
    else:
        players[0].append('RW')
        players[1].append('ST')
        players[2].append('LW')

def clean_formation(s):
    if not any([c.isnumeric() for c in s]):
        return -1
    else:
        total_players = 0
        implies_4 = ['linea', 'línea', 'lìnea', 'cuadrado', 'rombo', 'trapecio']
        ret = []
        no_parenthesis = s.strip('(/)')
        if '−' in no_parenthesis:
            split_by_hyphens = no_parenthesis.split('−')
        else:
            split_by_hyphens = no_parenthesis.split('-')
        for element in split_by_hyphens:
            if element.isnumeric():
                total_players += int(element)
                ret.append(element.lower())
            elif element.lower() in implies_4:
                total_players += 4
                if element.lower() in implies_4[:3]: # element is "linea" with some accent or without
                    ret.append('linea')
                else:
                    ret.append(element.lower())
            if total_players == 10:
                return '-'.join(ret)
    return -1

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
        name = name.replace('.', ',').replace(',,', ',')
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

def is_name(s):
    if s.isnumeric():
        return False
    if ',' not in s:
        return False
    comma_split = s.split(',')
    if len(comma_split) != 2:
        return False
    if any([len(name) < 2 for name in comma_split]):
        return False
    return True

url = 'https://docs.google.com/spreadsheets/u/0/d/1z690q2x2_exONCuVMZyaVghLMVrxmfnqllUjNaUAAjg/pub?single=true&gid=0&range=A1:O43&output=html'
response = requests.get(url)
html = response.text
parse(clean_table(html))
