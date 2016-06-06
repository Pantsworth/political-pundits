import bson
from functools import wraps
from flask import request, redirect, url_for
from connection import _content
from context.content import get_article
# from context.nlp.classifier import classify_text
# from context.nlp.entities import get_entities
# from context.nlp.keywords import get_keywords
# from auth import get_twitter_credentials
# from stakeholders import find_stakeholder_twitter_users
import requests
import httplib
import urlparse

from context.pundits import pundits

import newspaper


class InvalidRequest(Exception):
    status_code = 400


def all_the_content(content, article_database_ref, reload_pundits=False):
    """

    :param content: this is the mongo object containing our content up to now
    :param reload_pundits: if true, pundits are re-scraped every time
    :return: returns keywords, entities, and newpundits, as well as storing them in the mongo object for the article
    """

    reload_pundits = True

    article = newspaper.Article(content['url'])
    article.download()
    article.parse()
    article.nlp()

    print "HERE ARE THE NEWSPAPER KEYWORDS", article.keywords

    content['keywords']=""
    content['entities']=""

    # if not 'keywords' in content:
    #     content['keywords'] = [x for x in get_keywords(content['text'])
    #         if x['count'] > 2]
    #     _content.update({'_id': bson.ObjectId(content['id'])},
    #         {'$set': {'keywords': content['keywords']}})
    #
    # if not 'entities' in content:
    #     content['entities'] = get_entities(content['text'])
    #     _content.update({'_id': bson.ObjectId(content['id'])},
    #         {'$set': {'entities': content['entities']}})

    if not 'newpundits' in content or reload_pundits:
        content['newpundits'] = []
        dupe_list = []

        snippets, ratios = pundits.keyword_match(article_database_ref, article.keywords)
        content['newpundits'] = snippets

        _content.update({'_id': bson.ObjectId(content['id'])},
            {'$set': {'newpundits': content['newpundits']}})



    if not len(content['newpundits']):
        print "nothing to see here!"
        failed_snippet = {}
        failed_snippet['name'] = "#shambles"
        failed_snippet['text'] = "we can't seem to find anything."
        content['newpundits'] = [[failed_snippet]]
    else:
        print "HERE ARE NEW PUNDITS:", content['newpundits']

    return content['keywords'], content['entities'], content['newpundits']


# def content_keywords(content):
#     if not 'keywords' in content:
#         content['keywords'] = [x for x in get_keywords(content['text'])
#             if x['count'] > 2]
#         _content.update({'_id': bson.ObjectId(content['id'])},
#             {'$set': {'keywords': content['keywords']}})
#     return content['keywords']
#
#
# def content_entities(content):
#     if not 'entities' in content:
#         content['entities'] = get_entities(content['text'])
#         _content.update({'_id': bson.ObjectId(content['id'])},
#             {'$set': {'entities': content['entities']}})
#     return content['entities']
#
#
# def content_categories(content):
#     if not 'categories' in content:
#         content['categories'] = classify_text(content['text'])
#         _content.update({'_id': bson.ObjectId(content['id'])},
#             {'$set': {'categories': content['categories']}})
#     return content['categories']
#
#
# def content_stakeholders(content):
#     if not 'stakeholders' in content:
#         entities = content_entities(content)
#         kwargs = {
#             'credentials': get_twitter_credentials()
#         }
#         stakeholder_list = find_stakeholder_twitter_users(
#             entities, **kwargs)
#         content['stakeholders'] = stakeholder_list
#         _content.update({'_id': bson.ObjectId(content['id'])},
#             {'$set': {'stakeholders': content['stakeholders']}})
#     return content['stakeholders']


def cached_content(url=None, content_id=None, refresh=False):
    """
    Retrieve content from the cache or fetch it and cache it. Replaces
    Mongo's _id with id.  Will always fetch anew if refresh=True.

    returns json object with url, title, and text as fields.
    """
    if url:
        r = _content.find_one({'url': url})
    elif content_id:
        r = _content.find_one({'_id': bson.ObjectId(content_id)})
    else:
        raise Exception('No Content Identifier')
    if not r:
        data = get_article(url)
        r = {
            'url': url,
            'title': data['title'],
            'text': data['text'],
        }
        _content.insert(r, manipulate=True)  # so id is set
    elif refresh:
        data = get_article(url)
        update_r = {
            '_id': r['_id'],
            'url': url,
            'title': data['title'],
            'text': data['text'],
            'test': 'testing this function',
        }
        _content.save(update_r)
        r = update_r
    r['id'] = str(r['_id'])
    del r['_id']
    return r


def content_identifier_required(f):
    """
    Enforces id or url query parameter on a route.
    Accepts 'refresh' query parameter to reset cache
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        content_id = kwargs.get('content_id')
        if content_id is None:
            content_id = request.args.get('id')
        if not 'url' in request.args and content_id is None:
            if 'application/json' not in request.headers['Accept'] and \
                    request.args.get('_format') != 'json':
                return redirect(url_for('url_required') + \
                    '?next=%s' % request.script_root + request.path)
            else:
                raise InvalidRequest('url parameter is required')
        refresh = int(request.args.get('refresh', '0'))
        if content_id:
            r = cached_content(content_id=content_id, refresh=refresh)
        else:
            url = request.args.get('url')
            if not url:
                raise InvalidRequest('URL or content ID required.')
            r = cached_content(url=url, refresh=refresh)
        if not r:
            raise Exception('Could not find article content')
        request.content = r
        return f(*args, **kwargs)
    return wrapper


def require_url(f):
    """Enforces URL parameter on a route. Does not do content ID resolution
    or content lookup - for that use content_identifier_required."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not 'url' in request.args:
            return redirect(url_for('url_required') + \
                '?next=%s' % request.script_root + request.path)
        return f(*args, **kwargs)
    return wrapper


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