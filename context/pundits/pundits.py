import json
import requests
import bs4
import os
import newspaper
from newspaper import Article, ArticleException
import threading
import httplib
import urlparse
import nltk

results = []
url_duplicates = {}


def make_article_database():
    fn = os.path.join(os.path.dirname('__file__'), 'database/database.json')
    if not os.path.exists(fn):
        fn = os.getcwd()[:-3] + 'context/pundits/database/database.json'
        # print "fn is: ", fn
        # print "current working dir is", os.getcwd()

    with open(fn, "r") as json_file:
        database = json.loads(json_file.read())

    # print database
    return database


def keyword_match(article_database, keyword_list, n=5):
    """

    :param article_database: object containing JSON database (don't want to reload this every time
    :param keyword_list: list of keyword from the article
    :param n: number of matches to return. defaults to 5.
    :return:    article_list: list of relevant articles, to be stored in the Mongo object for the article.
                ratio_list: list of ratios for each article. not useful, but hey, it's there!
    """

    porter = nltk.PorterStemmer()

    if article_database==[]:
        print "making article database"
        article_database = make_article_database()


    new_keyword_list = []
    for word in keyword_list:
        new_keyword_list.append(porter.stem(word))

    keyword_list = sorted(new_keyword_list)
    print keyword_list


    ratio_list = []
    article_list = []

    for article in article_database['snippets']:

        new_list = []
        for word in article['keywords']:
            new_list.append(porter.stem(word))
        new_list = sorted(new_list)

        # print set(keyword_list).intersection(new_list)
        keyword_set = set(keyword_list).intersection(set(new_list))
        # print "keyword set is: ", keyword_set

        concordance_list = []
        # text = nltk.Text(article['text'])

        # for key in keyword_set:
        #     result = text.concordance(key)
        #     if result:
        #         concordance_list += str(result)
        # print concordance_list

        article['text'] = article['text'][:300] + "..."

        ratio = len(keyword_set) / float(len(set(keyword_list).union(new_list)))
        # ratio = len(set(keyword_list).intersection(new_list)) / float(len(set(keyword_list).union(new_list)))

        if len(ratio_list)<n and article not in article_list:
            ratio_list.append(ratio)
            article_list.append(article)
            # print ratio_list, article_list

        elif ratio > min(ratio_list) and article not in article_list:
            # print "ratio is:", ratio, "min was: ", min(ratio_list)
            index = ratio_list.index(min(ratio_list))
            ratio_list[index] = ratio
            article_list[index] = article
            # print ratio_list, article_list

        # print ratio, min(ratio_list)

        # print ratio, keyword_list,"\n", sorted(article['keywords'])
    print ratio_list, article_list
    return article_list, ratio_list



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
    # global results

    snippets = []
    global results
    results = []

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
                        if not url_duplicates.has_key(url):
                            process = threading.Thread(target=build_snippets, args=[query, link, url, snippet])
                            url_duplicates[url] = 1
                            process.start()
                            threads.append(process)
                        else:
                            print "thrown out url is: ", url
                            pass

    for process in threads:
        process.join()

    print "HERE ARE THE SNIPPETS:", results

    if n == -1:
        return results
    else:
        sorted_snippets = sorted(results, key=lambda k: k['relevance'])
        return sorted_snippets[:n]



def build_snippets(query, website, url, snippet):
    '''
    takes in the query, website, url, and snippet, and constructs the full snippet
    '''
    # snippets = []
    snippet['source'] = website
    global results

    # print "BUILDING SNIPPETS...\n"
    if website == "cfr":
        # print "FROM CFR..."
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
                        snippet['relevance'] = article.text.count(query)
            else:
                break

    elif website == "twitter":
        # print "FROM TWITTER...\n"
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
        # print "FROM BROOKINGS...\n"
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
                # print "relevant article"
                snippet['text'] = article.summary
                snippet['url'] = full_url
                snippet['relevance'] = article.text.count(query)

    print "DONE WITH SNIPPETS FOR: ", snippet['name']
    # print snippet

    if 'text' in snippet:
        if snippet not in results:
            results.append(snippet)
            return snippet
        else:
            print "snippet already in results"
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
    # test to make sure we get nothing the second time:
    keyword_match(make_article_database(), None)

    # print "snippets_1", snippets_1
    # print "snippets_2", snippets_2
    # print "results are: ", results
    print "done"
