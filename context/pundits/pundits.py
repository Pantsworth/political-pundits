import json
import requests
import bs4
import os
from newspaper import Article, ArticleException
import threading
import httplib
import urlparse

results = []
url_duplicates = []

def retrieve_snippets(query):
    '''
    takes in a query (keyword) and returns a list of relevant snippets if that keyword exists, else returns false
    snippets are dictionaries with the following keys:
        name: name of pundit
        title: the pundit's credentials
        keyword: query keyword
        source: where the text came from (twitter or cfr)
        url: url to the full text (article or tweet)
        text: body of the snippet
    '''
    global results



    snippets = []
    fn = os.path.join(os.path.dirname('__file__'), 'panel/panel.json')
    if not os.path.exists(fn):
        fn = os.getcwd()[:-3] + 'context/pundits/panel/panel.json'
        # print "fn is: ", fn
        # print "current working dir is", os.getcwd()

    with open(fn, "r") as json_file:
        panel = json.loads(json_file.read())
        threads = []

        if query in panel.keys():
            print "FOUND RESULTS FOR ", query
            results = []
            for user in panel[query]:
                #create a list of threads
                # In this case 'urls' is a list of urls to be crawled.
                    # We start one thread per url present.
                for link in user['links']:
                    if user['links'][link]:
                        snippet = {}
                        snippet['name'] = user['name']
                        snippet['title'] = user['title']
                        snippet['keyword'] = query
                        url = user['links'][link]
                        print "WORKING ON SNIPPETS FROM", user['name'], "\n"
                        process = threading.Thread(target=build_snippets, args=[query, link, url, snippet])
                        process.start()
                        threads.append(process)

            for process in threads:
                process.join()

        #         # At this point, results for each URL are now neatly stored in order in 'results'
        #         for link in user['links']:
        #             if user['links'][link]:
        #                 snippet = {}
        #                 snippet['name'] = user['name']
        #                 snippet['title'] = user['title']
        #                 snippet['keyword'] = query
        #                 url = user['links'][link]
        #                 print "WORKING ON SNIPPETS FROM", user['name']
        #                 snippet_search_result = build_snippets(query, link, url, snippet)
        #                 if snippet_search_result:
        #                     snippets.append(snippet_search_result)
        #                 print "SNIPPETS SO FAR:", snippets
        # else:
        #     return False

    print "HERE ARE THE SNIPPETS:", results
    return results


def build_snippets(query, website, url, snippet):
    '''
    takes in the query, website, url, and snippet, and constructs the full snippet
    '''
    # snippets = []
    snippet['source'] = website
    global results
    if url in url_duplicates:
        print "caught duplicate url"
    else:
        url_duplicates.append(url)

    print "BUILDING SNIPPETS...\n"
    if website == "cfr":
        print "FROM CFR..."
        response = requests.get(url + "#publications")
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        article_count = 0
        for article in soup.select('article.publication_spotlight h3 a'):
            if article_count < 6:
                href = str(article.attrs.get('href'))
                full_url = "http://www.cfr.org/" + href
                if validate_url(full_url):
                    article = Article(full_url)
                    article.download()
                    article.parse()
                    article_count += 1
                    try:
                        article.nlp()
                    except ArticleException():
                        return False
                    if query in article.keywords:
                        snippet['text'] = article.summary
                        snippet['url'] = full_url
            else:
                break

    elif website == "twitter":
        print "FROM TWITTER...\n"
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

    elif website == "brookings":
        print "FROM BROOKINGS...\n"
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

    print "DONE WITH SNIPPETS FOR: ", snippet['name']
    if 'text' in snippet:
        results.append(snippet)
        return snippet

    else:
        return False



def get_server_status_code(url):
    """
    Download just the header of a URL and
    return the server's status code.
    """
    # http://stackoverflow.com/questions/1140661
    host, path = urlparse.urlparse(url)[1:3]    # elems [1] and [2]
    try:
        conn = httplib.HTTPConnection(host)
        conn.request('HEAD', path)
        return conn.getresponse().status
    except StandardError:
        return None


def validate_url(url):
    """
    Check if a URL exists without downloading the whole file.
    We only check the URL header.
    """
    # see also http://stackoverflow.com/questions/2924422
    good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
    return get_server_status_code(url) in good_codes


if __name__ == '__main__':
    print retrieve_snippets('syria')
    # print "results are: ", results
    print "done"
