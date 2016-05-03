import requests
import bs4
import re
import json

website = "http://america.aljazeera.com"
response = requests.get(website + "/topics/topic/categories/international.html")
soup = bs4.BeautifulSoup(response.text, "html.parser")

links = []

page = 1

while len(links) < 1:
    for a in soup.select('h3.headline a'):
        href = str(a.attrs.get('href'))
        if not re.match(r'^/watch', href):
            if not re.match(r'^http', href):
                url = website + a.attrs.get('href')
            else:
                url = a.attrs.get('href')
            link = {}
            link['url'] = url
            links.append(link)
            print link

        page += 1

        response = requests.get(website + "/topics/topic/categories/international.html%3Fpage=" + str(page))
        soup = bs4.BeautifulSoup(response.text, "html.parser")

with open('corpus.json', 'r+w') as outfile:
    # corpus = json.load(outfile)
    # corpus.append(links)
    json.dump(links, outfile)
