import requests
import bs4
import re
import json
from newspaper import Article
from time import sleep

num_links_per = 1000
nap_time = 5

links = []

# the atlantic
website = "http://www.theatlantic.com"

page = 1

atlantic_links = []
while len(atlantic_links) < num_links_per:
    response = requests.get(website + "/international?page=" + str(page))
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    for a in soup.select('li.article a'):
        href = str(a.attrs.get('href'))

        if re.match(r'^/international', href) and not re.match(r'^(.*)disqus_thread', href) and len(re.findall(r'/', href)) > 3:
            link = {}
            url = website + a.attrs.get('href')
            link['url'] = url
            articule_response = requests.get(url)
            # article_soup = bs4.BeautifulSoup(articule_response.text, "html.parser")
            #
            # link['text'] = article_soup.find('div', {'class': 'article-body'}).getText()
            article = Article(url)
            article.download()
            article.parse()
            link['text'] = article.text
            article.nlp()
            link['keywords'] = article.keywords
            atlantic_links.append(link)
            print link

    page += 1

links += atlantic_links

# aljazeera america
website = "http://america.aljazeera.com"
response = requests.get(website + "/topics/topic/categories/international.html")
soup = bs4.BeautifulSoup(response.text, "html.parser")

page = 1

aljazeera_links = []
while len(aljazeera_links) < num_links_per:
    for a in soup.select('h3.headline a'):
        href = str(a.attrs.get('href'))
        if not re.match(r'^/watch', href):
            if not re.match(r'^http', href):
                url = website + a.attrs.get('href')
            else:
                url = a.attrs.get('href')
            link = {}
            link['url'] = url
            article = Article(url)
            article.download()
            article.parse()
            link['text'] = article.text
            article.nlp()
            link['keywords'] = article.keywords

            aljazeera_links.append(link)
            print link

        page += 1

        try:
            response = requests.get(website + "/topics/topic/categories/international.html%3Fpage=" + str(page))
            soup = bs4.BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.ConnectionError:
            time.sleep(nap_time)
            response = requests.get(website + "/topics/topic/categories/international.html%3Fpage=" + str(page))
            soup = bs4.BeautifulSoup(response.text, "html.parser")


links += aljazeera_links

# reuters
website = "http://www.reuters.com"

page = 1

reuters_links = []
while len(reuters_links) < num_links_per:
    try:
        response = requests.get(website + "/news/archive/worldNews?view=page&page=" + str(page))
        soup = bs4.BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.ConnectionError:
        time.sleep(nap_time)
        response = requests.get(website + "/news/archive/worldNews?view=page&page=" + str(page))
        soup = bs4.BeautifulSoup(response.text, "html.parser")

    for a in soup.select('h3.story-title a'):
        href = str(a.attrs.get('href'))
        link = {}
        link['url'] = url
        article = Article(url)
        article.download()
        article.parse()
        link['text'] = article.text
        article.nlp()
        link['keywords'] = article.keywords

        reuters_links.append(link)
        print link

    page += 1

links += reuters_links

with open('corpus.json', 'w') as outfile:
    json.dump(links, outfile)
