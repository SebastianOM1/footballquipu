import requests
from bs4 import BeautifulSoup
import os
import getallurls

def main():
    print('Start reading at:')
    start_to_read = int(input())
    print('Read for how long:')
    read_how_many = int(input())
    links = open('scraping\central_links.txt', 'r')
    queue = []
    for i in range(start_to_read + read_how_many):
        queue.append(links.readline().rstrip())
    
    for url in queue[start_to_read:start_to_read+read_how_many]:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        competition(url, soup)
    
    links.close()
    
def competition(url, soup):
    # Get year
    name = soup.find('span', attrs={'class':'componentheading'}).text.strip().replace('- ', '')
    wordArr = name.split(' ') # ['Descentralizado', '2012']
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
    links = getallurls.main(url, soup)
    for link in links:
        name = link.split('/')[-1]
        complete_name = os.path.join(pat, name + '.txt')
        html = getallurls.get_html(link)
        with open(complete_name, 'w') as file:
            file.write(html)

if __name__ == '__main__':
    main()