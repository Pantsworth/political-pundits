import requests
import bs4
import re
import json

website = "http://www.reuters.com"

links = []

page = 1

while len(links) < 1:
    response = requests.get(website + "/news/archive/worldNews?view=page&page=" + str(page))
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    for a in soup.select('h3.story-title a'):
        href = str(a.attrs.get('href'))
        link = {}
        link['url'] = website + a.attrs.get('href')
        links.append(link)
        print link

    page += 1

with open('corpus.json', 'r+w') as outfile:
    corpus = json.load(outfile)
    corpus.append(links)
    json.dump(corpus, outfile)
