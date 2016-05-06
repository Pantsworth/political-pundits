import json
import requests
import bs4
from newspaper import Article

def get_relevant_articles(query):
    with open('panel/panel.json', "r") as json_file:
        panel = json.loads(json_file.read())
        for keyword in panel:
            if keyword == query:
                for user in panel[keyword]:
                    # print user['name']
                    for link in user['links']:
                        if user['links'][link]:
                            snippet = {}
                            snippet['name'] = user['name']
                            snippet['keyword'] = query
                            url = user['links'][link]
                            # print "\t" + url
                            get_relevant_text(query, link, url, snippet)

def get_relevant_text(query, website, url, snippet):
    query = query.lower()
    snippet['source'] = website
    if website == "cfr":
        response = requests.get(url + "#publications")
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        # print "\t\t" + url + "#publications"
        for article in soup.select('article.publication_spotlight h3 a'):
            href = str(article.attrs.get('href'))
            full_url = "http://www.cfr.org/" + href
            article = Article(full_url)
            article.download()
            article.parse()
            article.nlp()
            # print article.keywords
            if query in article.keywords:
                snippet['text'] = article.summary
                snippet['url'] = full_url
                print snippet
    elif website == "twitter":
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for tweet in soup.select('div.tweet'):
            if tweet.select('div.content p.tweet-text'):
                tweet_content = tweet.select('div.content p.tweet-text')[0].text
                if tweet.select('small.time a'):
                    tweet_url = tweet.select('small.time a')[0].attrs.get('href')
                    tweet_content_lower = tweet_content.lower()
                    if query in tweet_content:
                        snippet['text'] = tweet_content
                        snippet['url'] = "http://twitter.com" + tweet_url
                        print snippet
