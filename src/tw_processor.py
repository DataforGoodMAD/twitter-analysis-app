import logging
import re
import unicodedata
from collections import Counter
from statistics import mean

import es_core_news_md  # spaCy pretrained model
import nltk
import pandas as pd
import spacy
from nltk.stem import WordNetLemmatizer

from db_queries import DBQueries

try:
    from nltk.corpus import stopwords
except:
    nltk.download("stopwords")
    from nltk.corpus import stopwords


logger = logging.getLogger('debug_logger')
logger.info('logger working')


class TwitterProcessor:
    # TODO: revisar idioma del lemmatizer. Configuración de idioma.
    def __init__(self, counter=Counter(), lemmatizer=WordNetLemmatizer()):

        self.__counter = counter
        self.lemmatizer = lemmatizer
        self.punctuation = '¡!"$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        self.stopWords = set(stopwords.words(
            'spanish') + stopwords.words('english'))
        self.nlp = es_core_news_md.load()

        # DB Connection
        self.db_queries = DBQueries()

    def __repr__(self):
        return(f"""
        TweetsProcessor object:
        Counter: {self.__counter}
        Lemmatizer: {self.lemmatizer}
        """)

    def __str__(self):
        return(f"TweetsProcessor object")

    def addStopWords(self, lst):
        self.stopWords.update(set(lst))
        return f'Added to stopwords: {lst}'

    def tweetTokenizer(self, tweet_text):
        """
        Makes lowercase.
        Removes punctuation, stopwords, urls & numerics.
        Lemmatize.
        Returns a list of tokens.
        """

        tweet = re.sub(r'http\S*', '', tweet_text)  # remove URLs
        tweet = unicodedata.normalize(
            'NFKD', tweet).encode('ASCII', 'ignore').decode('utf-8')  # remove accents
        words = str(tweet).translate(str.maketrans('', '', self.punctuation)
                                     ).lower().split()  # lowercase & punctuation
        token_list = [self.lemmatizer.lemmatize(word)
                      for word in words
                      if word not in self.stopWords and not word.isnumeric() and len(word) > 2]  # lemmatizee, remove numerics & remove tokens with less than 3 letters.

        logger.info(f'Tokens created: {token_list}')

        return token_list

    @property
    def counter(self):
        return self.__counter

    def updateCounter(self, token_list):
        self.counter.update(token_list)
        return self.__counter

    def toSpacyDocs(self, batch_of_tweets):
        with self.nlp.disable_pipes(self.nlp.pipe_names):
            docs = [doc for doc in self.nlp.pipe(
                [" ".join(self.tweetTokenizer(tweet.full_text)) for tweet in batch_of_tweets]) if doc.vector_norm]
        return docs

    @property
    def userRefDocs(self):
        user_tweets = self.db_queries.getUserTweets(limit=50)
        return self.toSpacyDocs(user_tweets)


if __name__ == "__main__":
    p = TwitterProcessor()
    p
