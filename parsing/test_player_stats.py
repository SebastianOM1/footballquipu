import os
from parse import parse, clean_table

mainfolder = os.path.abspath(os.curdir)
datafolder = os.path.join(mainfolder, 'scraping', 'data')

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
                    formation1 = results['Team 1 Formation']
                    formation2 = results['Team 2 Formation']
                    if formation1 in formations:
                        formations[formation1] += 1
                    else:
                        formations[formation1] = 1
                        print(formation2, '-', year, competition, file)
                    if formation2 in formations:
                        formations[formation2] += 1
                    else:
                        formations[formation2] = 1
                        print(formation2, '-', year, competition, file)
            except Exception as e:
                    pass

print(formations)