import requests
from bs4 import BeautifulSoup
import os
import getallurls
from getallurls import *

def main():
    urls = [
        'https://dechalaca.com/fichas/liga1-fase-2-2021-/',
        'https://dechalaca.com/fichas/definiciones-2021/'
    ]
    
    for url in urls:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        competition(url, soup)
    
def competition(url, soup):
    # Get year
    name = soup.find('span', attrs={'class':'componentheading'}).text.strip().replace('- ', '')
    wordArr = name.split(' ')
    yearIndex = 0
    for i in range(len(wordArr)):
        if not wordArr[i].isalpha() and wordArr[i] != '1' and wordArr != '2':
            yearIndex = i
    year = wordArr.pop(yearIndex)
    competition_name = ' '.join(wordArr)
    # Within corresponding year folder, create competition subfolder
    pat = os.path.join('scraping', 'data', year, competition_name)
    if not os.path.exists(pat):
        os.mkdir(pat)
    links = getLinks(url, soup)
    for link in links:
        name = link.split('/')[-1]
        complete_name = os.path.join(pat, name + '.txt')
        html = getallurls.get_html(link)
        with open(complete_name, 'w') as file:
            file.write(html)

def getLinks(url, soup):
    no_tildes = lambda x: x.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    teams = get_teams(soup)
    links = set()
    for team in teams:
        team_parameter = '%20'.join([word.lower() for word in team.split(' ')])
        new_url = url + 'pagina-1-20?filter=' + no_tildes(team_parameter) + '&order=rdate'
        response = requests.get(new_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        get_links_in_page(soup, links)
    return links

if __name__ == '__main__':
    main()