import requests
from bs4 import BeautifulSoup
import os
import getallurls

def main():
    mainfolder = os.path.abspath(os.curdir)
    datafolder = os.path.join(mainfolder, 'scraping', 'data')
    
    links = []
    for year in os.listdir(datafolder):
        yearfolder = os.path.join(datafolder, year)
        files = os.listdir(yearfolder)
        for file in files:
            if '.txt' in file:
                links.append(file)
    
    print('(A) Read all (B) Read some: ')
    choice = input()
    if choice == 'A':
        read_all(links, datafolder)
    else:
        pass

def read_all(links, datafolder):
    for link in links:
        year, competition = link.split('_')
        year = year.replace('links', '')
        competition = competition.replace('.txt', '')
        savefolder = os.path.join(datafolder, year, competition.title())
        with open(os.path.join(datafolder, year, link), 'r') as txt_file:
            urls = txt_file.readlines()
            urls = [url.rstrip() for url in urls]
            for url in urls:
                name = url.split('/')[-1]
                if year != '2016':
                    competition = competition.title() if competition != 'fase2' else 'Fase 2'
                    savefolder = os.path.join(datafolder, year, 'Liga 1 ' + competition)
                complete_name = os.path.join(savefolder, name + '.txt')
                html = get_html(url)
                with open(complete_name, 'w', encoding="utf-8") as iframe_data:
                    iframe_data.write(html)
            
def get_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    iframe = soup.find('iframe')
    source = iframe['src'].strip()
    html = requests.get(source).text
    return html

if __name__ == '__main__':
    main()