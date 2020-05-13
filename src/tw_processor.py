import re
import logging
import unicodedata
from collections import Counter
import pandas as pd


import nltk
from nltk.stem import WordNetLemmatizer
try:
    from nltk.corpus import stopwords
except:
    nltk.download("stopwords")
    from nltk.corpus import stopwords


logger = logging.getLogger('debug_logger')
logger.info('logger working')


class TwitterProcessor:

    def __init__(self, counter=Counter(), lemmatizer=WordNetLemmatizer()):

        self.__counter = counter
        self.lemmatizer = lemmatizer
        self.punctuation = '¡!"$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        self.stopWords = set(stopwords.words(
            'spanish') + stopwords.words('english'))

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
                      if word not in self.stopWords and not word.isnumeric() and len(word) > 2]  # lemmatize & remove numerics

        logger.info(f'Tokens created: {token_list}')

        return token_list

    def getTweetHashtags(self, tweet_text):
        tokens = self.tweetTokenizer(tweet_text)
        return re.findall(r'#\w+', tokens)

    @property
    def counter(self):
        return self.__counter

    def updateCounter(self, token_list):
        self.counter.update(token_list)

    def getMostCommonTokens(self, top=10):
        return self.counter.most_common()[0:top]

    def loadCounterFromDB(self):
        pass
