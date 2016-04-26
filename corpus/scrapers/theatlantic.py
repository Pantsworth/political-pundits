import requests
import bs4
import re

website = "http://www.theatlantic.com"

links = []

page = 1

while len(links) < 1000:
    response = requests.get(website + "/international?page=" + str(page))
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    for a in soup.select('li.article a'):
        href = str(a.attrs.get('href'))

        if re.match(r'^/international', href) and not re.match(r'^(.*)disqus_thread', href) and len(re.findall(r'/', href)) > 3:
            links.append(website + a.attrs.get('href'))

    page += 1



print links
