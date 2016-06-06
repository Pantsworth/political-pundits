Political-Pundits is a web application based on the Knight Lab's Context toolkit. It is designed to provide additional depth to the reader of a news article by offering them expert additions to the story from a hand-curated set of experts in the domain of foreign policy.

To use it, the reader simply takes a URL for an article they'd like to get expert opinions on and drops it into our input field. After a few seconds, the Political Pundits app will respond with a compact page that contains both the full text of the article as well as content from experts writing about the same topic.

Political Pundits is functional for any input URL that can be read by the newspaper web scraping python library. If you encounter an error, it is likely a result of updates or modifications to said library or the news site being accessed.




# NU Infolab News Context Project

context is a suite of Python based tools for managing contextual knowledge related to web content. This includes resources for article text and metadata extraction from web pages, keyword and named entity extraction, and more.

The primary entry point is a Flask based web application that serves both HTML and JSON payloads. This application is located in the web directory.

context itself, under the context directory, may also be used directly as a python library.  

# About

A number of projects at NU Knightlab involve experiments in the space of evaluating contextual information related to web content in order to enhance user experience. This toolkit brings a number of those explorations into a single project space where they can be further explored and expanded.


# Requirements

In order to install lxml, you will need the development packages libxml2 and libxsl:

```
sudo apt-get install libxml2-dev libxslt-dev
```

In order to use the categorizer, you will need to [liblinear](http://www.csie.ntu.edu.tw/%7Ecjlin/liblinear/).

Ubuntu/Debian: ```sudo apt-get install liblinear1```

Mac OS:  should be able to use the included liblinear.so.1


# NLTK Resource requirements

The following resources should be installed with the NLTK downloader:

  * wordnet
  * words
  * maxent_treebank_pos_tagger
  * punkt
  * maxent_ne_chunker
  * stopwords

To use the downloader:

```
>>> import nltk
>>> nltk.download()
```
