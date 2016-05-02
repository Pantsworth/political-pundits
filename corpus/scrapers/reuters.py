import requests
import bs4
import re

website = "http://www.reuters.com"

links = []

page = 1

while len(links) < 1000:
    response = requests.get(website + "/news/archive/worldNews?view=page&page=" + str(page))
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    for a in soup.select('h3.story-title a'):
        href = str(a.attrs.get('href'))
        links.append(website + a.attrs.get('href'))
        print href

    page += 1

# print links
