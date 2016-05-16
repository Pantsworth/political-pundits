import json
import requests
import bs4
import os
from newspaper import Article


def retrieve_snippets(query, n=-1):
    '''
    takes in:
        query: keyword (string)
        n: number of snippets to return (if -1, will return all snippets)
    and returns a list of relevant snippets if that keyword exists

    snippets are dictionaries with the following keys:
        name: name of pundit
        title: the pundit's credentials
        keyword: query keyword
        source: where the text came from (twitter or cfr)
        url: url to the full text (article or tweet)
        text: body of the snippet
        relevance: number of times that query appears in the snippet text
    '''

    snippets = []
    fn = os.path.join(os.path.dirname('__file__'), 'panel/panel.json')

    with open(fn, "r") as json_file:
        panel = json.loads(json_file.read())

        if query in panel.keys():
            print "FOUND RESULTS FOR ", query
            for user in panel[query]:
                for link in user['links']:
                    if user['links'][link]:
                        snippet = {}
                        snippet['name'] = user['name']
                        snippet['title'] = user['title']
                        snippet['keyword'] = query
                        url = user['links'][link]
                        print "WORKING ON SNIPPETS FROM", user['name']
                        snippet_search_result = build_snippets(query, link, url, snippet)
                        if snippet_search_result:
                            snippets.append(snippet_search_result)
                        print "SNIPPETS SO FAR:", snippets
        else:
            return False

    print "HERE ARE THE SNIPPETS:", snippets
    
    if n == -1:
        return snippets
    else:
        sorted_snippets = sorted(snippets, key=lambda k: k['relevance'])
        return sorted_snippets[:n]


def build_snippets(query, website, url, snippet):
    '''
    takes in the query, website, url, and snippet, and constructs the full snippet
    '''
    snippet['source'] = website

    print "BUILDING SNIPPETS..."
    if website == "cfr":
        print "FROM CFR..."
        response = requests.get(url + "#publications")
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for article in soup.select('article.publication_spotlight h3 a'):
            href = str(article.attrs.get('href'))
            full_url = "http://www.cfr.org/" + href
            article = Article(full_url)
            article.download()
            article.parse()
            article.nlp()
            if query in article.keywords:
                snippet['text'] = article.summary
                snippet['url'] = full_url
                snippet['relevance'] = article.text.count(query)

    elif website == "twitter":
        print "FROM TWITTER..."
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
                        snippet['relevance'] = tweet_content.count(query)

    elif website == "brookings":
        print "FROM BROOKINGS..."
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for article in soup.select('ul.media-list li div.content h3.title a'):
            href = str(article.attrs.get('href'))
            full_url = "http://www.brookings.edu" + href
            article = Article(full_url)
            article.download()
            article.parse()
            article.nlp()
            if query in article.keywords:
                print "relevant article"
                snippet['text'] = article.summary
                snippet['url'] = full_url
                snippet['relevance'] = article.text.count(query)

    print "DONE WITH SNIPPETS"
    if 'text' in snippet:
        return snippet
    else:
        return False
