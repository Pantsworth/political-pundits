import requests
import bs4
import re

website = "http://america.aljazeera.com"
response = requests.get(website + "/topics/topic/categories/international.html")
soup = bs4.BeautifulSoup(response.text, "html.parser")

links = []

page = 1

while len(links) < 1000:
    for a in soup.select('h3.headline a'):
        href = str(a.attrs.get('href'))
        if not re.match(r'^/watch', href):
            if not re.match(r'^http', href):
                links.append(website + a.attrs.get('href'))
            else:
                links.append(a.attrs.get('href'))
            print href

        page += 1

        response = requests.get(website + "/topics/topic/categories/international.html%3Fpage=" + str(page))
        soup = bs4.BeautifulSoup(response.text, "html.parser")

print links
