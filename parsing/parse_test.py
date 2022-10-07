import os
from parse import parse, clean_table

success = 0
mainfolder = os.path.abspath(os.curdir)
datafolder = os.path.join(mainfolder, 'scraping', 'data')
exceptions = open('exceptions.txt', 'w')

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
                    parse(clean_table(html))
                    success += 1
            except Exception as e:
                    exceptions.write(year + ' ' + competition + ' ' + file + '\n')
exceptions.close()

print('Success:', success)
print('Exceptions:', exceptions)