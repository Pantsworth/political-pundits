import os
import json
import requests
import bs4
import httplib
import urlparse
from newspaper import Article, ArticleException

def build_db():
	fn = os.path.join(os.path.dirname('__file__'), '../panel/panel.json')
	db = {}
	db['snippets'] = []

	with open(fn, "r") as json_file:
		panel = json.loads(json_file.read())

		with open("database.json", "w") as outfile:
			i = 0
			for key in panel:
				i += 1
				j = 0
				print 'looking at {}, {}/{} keywords'.format(key, i, len(panel))

				for pundit in panel[key]:
					j += 1
					print '\tlooking at {}, {}/{} pundits'.format(pundit['name'], j, len(panel[key]))

					if pundit['links']['brookings']:
						response = requests.get(pundit['links']['brookings'])
						soup = bs4.BeautifulSoup(response.text, "html.parser")
						for link in soup.select('ul.media-list li div.content h3.title a'):
							snippet = {}
							link_href = str(link.attrs.get('href'))
							url = "http://www.brookings.edu" + link_href

							try:
								link_response = requests.get(url)
								soup = bs4.BeautifulSoup(link_response.text, "html.parser")						

								try:
									full_url_link = soup.select('div.article-detail em a')[0]
									full_url = str(full_url_link.attrs.get('href'))
								except IndexError:
									full_url = url

								article = Article(url)
								
								try:
									article.download()
									article.parse()
									article.nlp()

									print '\t\t', full_url
									snippet["text"] = article.text
									snippet["summary"] = article.summary
									snippet["url"] = url
									snippet["full_url"] = full_url
									snippet["keywords"] = article.keywords

									snippet["pundit"] = {}
									snippet["pundit"]["name"] = pundit["name"]
									snippet["pundit"]["title"] = pundit["title"]
									db['snippets'].append(snippet)
								except ArticleException():
									pass
							except requests.exceptions.ConnectionError:
								pass

					if pundit['links']['cfr']:
						response = requests.get(pundit['links']['cfr'] + "#publications")
						soup = bs4.BeautifulSoup(response.text, "html.parser")
						for link in soup.select('article.publication_spotlight h3 a'):
							snippet = {}
							link_href = str(link.attrs.get('href'))

							if "http" in link_href:
								full_url = link_href
								url = link_href
							else:
								url = "http://www.cfr.org" + link_href
								link_response = requests.get(url)
								soup = bs4.BeautifulSoup(link_response.text, "html.parser")

								try: 
									full_url_link = soup.select('section.publication article p a')[0]
									full_url = str(full_url_link.attrs.get('href'))
								except IndexError:
									full_url = url

							if 'pdf' not in full_url:
								article = Article(full_url)
							else:
								article = Article(url)
							
							try:
								article.download()
								article.parse()
								article.nlp()

								print '\t\t', full_url
								snippet["text"] = article.text
								snippet["summary"] = article.summary
								snippet["url"] = url
								snippet["full_url"] = full_url
								snippet["keywords"] = article.keywords

								snippet["pundit"] = {}
								snippet["pundit"]["name"] = pundit["name"]
								snippet["pundit"]["title"] = pundit["title"]
								db['snippets'].append(snippet)
							except ArticleException:
								pass

			json.dump(db, outfile, indent=4)

if __name__ == '__main__':
    build_db()