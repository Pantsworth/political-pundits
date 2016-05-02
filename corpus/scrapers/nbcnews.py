import requests
import bs4
import re

website = "http://www.nbcnews.com"

response = requests.get(website + "/news/world")
soup = bs4.BeautifulSoup(response.text, "html.parser")

links = []

for a in soup.select('div.panel a'):
    href = str(a.attrs.get('href'))
    if not re.match(r'video', href) and not re.match(r'^http', href) and len(re.findall(r'/', href)) > 2:
        links.append(website + a.attrs.get('href'))

print links
