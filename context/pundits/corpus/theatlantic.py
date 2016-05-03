import requests
import bs4
import re
import json

website = "http://www.theatlantic.com"

links = []

page = 1

while len(links) < 1:
    response = requests.get(website + "/international?page=" + str(page))
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    for a in soup.select('li.article a'):
        href = str(a.attrs.get('href'))

        if re.match(r'^/international', href) and not re.match(r'^(.*)disqus_thread', href) and len(re.findall(r'/', href)) > 3:
            link = {}
            link['url'] = website + a.attrs.get('href')
            links.append(link)
            print link

    page += 1

with open('corpus.json', 'r+w') as outfile:
    corpus = json.load(outfile)
    corpus.append(links)
    json.dump(corpus, outfile)
