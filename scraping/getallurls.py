import requests
from bs4 import BeautifulSoup
import re

def main(competition_url, soup):
    no_tildes = lambda x: x.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    teams = get_teams(soup)
    links = set()
    for team in teams:
        team_parameter = '%20'.join([word.lower() for word in team.split(' ')])
        url = competition_url + 'pagina-1-30?filter=' + no_tildes(team_parameter) + '&order=rdate'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        get_links_in_page(soup, links)
    return links

def get_links_in_page(soup, links):
    rows = soup.find_all('tr', attrs={'class': re.compile("sectiontableentry")})
    link_in_row = [row.find('a')['href'] for row in rows]
    for link in link_in_row:
        links.add(link)

def get_teams(soup):
    rows = soup.find_all('tr', attrs={'class': re.compile("sectiontableentry")})
    title_in_row = [row.find('a').text for row in rows]
    clean_titles = [title.strip() for title in title_in_row]
    teams = set()
    for title in clean_titles:
        a, b = title.split('-')
        teams.add(a.replace('FINAL:', '').strip()[:-1].strip())
        teams.add(b[:-1].strip())
    return teams

def get_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    iframe = soup.find('iframe')
    source = iframe['src'].strip()
    html = requests.get(source).text
    return html