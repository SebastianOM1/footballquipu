import os
from parse import parse, clean_table

mainfolder = os.path.abspath(os.curdir)
datafolder = os.path.join(mainfolder, 'scraping', 'data')
cities = dict()

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
                    city = results['City']
                    if city in cities:
                        cities[city] += 1
                    else:
                        cities[city] = 1
            except Exception as e:
                    pass

print(cities)