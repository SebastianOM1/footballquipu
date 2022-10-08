import os
from parse import parse, clean_table, is_name

mainfolder = os.path.abspath(os.curdir)
datafolder = os.path.join(mainfolder, 'scraping', 'data')
success = 0
wrong = 0
wrong_set = set()

for year in os.listdir(datafolder):
    yearfolder = os.path.join(datafolder, year)
    for competition in os.listdir(yearfolder):
        competitionfolder = os.path.join(yearfolder, competition)
        for file in os.listdir(competitionfolder):
            try:
                txt_file = open(os.path.join(competitionfolder, file), 'r')
                html = txt_file.read()
            except Exception as e:
                txt_file = open(os.path.join(competitionfolder, file), 'r', encoding='utf-8')
                html = txt_file.read()
            try:
                    results = parse(clean_table(html))
                    starting1, starting2 = results['Starting eleven 1'], results['Starting eleven 2']
                    subs1, subs2 = results['Subs 1'], results['Subs 2']
                    players = starting1 + starting2 + subs1 + subs2
                    for player in players:
                        if is_name(player[0]):
                            success += 1
                        else:
                            wrong += 1
                            wrong_set.add((player[0], year + competition + file))
            except Exception as e:
                    pass    

print(success / (success + wrong), '%% of players have a name')
print('Examples of wrong cases:')
for example in list(wrong_set)[:10]:
    print(example)
