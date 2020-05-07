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
        self.__lemmatizer = lemmatizer
        self.__punctuation = '¡!"$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        self.__stopWords = set(stopwords.words('spanish') + stopwords.words('english'))

    def __repr__(self):
        return(f"""
        TweetsProcessor object:
        Counter: {self.__counter}
        Lemmatizer: {self.__lemmatizer}
        """)

    def __str__(self):
        return(f"TweetsProcessor object")

    def addStopWords(self, lst):
        self.__stopWords.update(set(lst))
        return f'Added to stopwords: {lst}'

    def tweetPreprocessor(self, tweet):
        """
        Makes lowercase. 
        Removes punctuation, stopwords, urls & numerics. 
        Lemmatize.
        Returns a list of tokens.
        """

        tweet = re.sub(r'http\S*', '', tweet) #remove URLs
        tweet = unicodedata.normalize(
                'NFKD', tweet).encode('ASCII', 'ignore').decode('utf-8') #remove accents
        words = str(tweet).translate(str.maketrans('', '', punctuation)).lower().split() #lowercase & punctuation
        token_list = [lemmatizer.lemmatize(word) 
                        for word in words 
                        if word not in stop_words and not word.isnumeric() and len(word) > 2] #lemmatize & remove numerics
        
        logger.info(f'Tokens created: {token_list}')

        return token_list

    def updateCounter(self, token_list):
        self.__counter.update(token_list)
        print()

    def getMostCommonTokens(self, top=10):
        return self.__counter.most_common()[0:top]

    def getTweetHashtags(self, tweet_text):
        
        return 

    


        


# ################
# try:
#     from nltk.corpus import stopwords
# except:
#     nltk.download("stopwords")
# from nltk.tokenize import word_tokenize, wordpunct_tokenize
# from nltk.stem import SnowballStemmer
# import nltk
# import spacy
# import unicodedata


# def prep_text(text, p):
#     p.set_text(text)
#     p.pipeline()
#     return p.get_text(), p

# def prep_tweets(row, p):
#     row['processed_text'], p = prep_text(row['tweet'], p)
#     row['processed_tokens'] = p.get_tokens()
#     return row

# class Preprocessor():
#     def __init__(self, language='english', language_code='en', bad_list=[], bad_root_list=[]):
#         self.__stopwords = stopwords.words(language)
#         self.__stemmer = SnowballStemmer(language)
#         self.__lemm = spacy.blank(language_code)
#         self.__bad_list = bad_list
#         self.__bad_root = bad_root_list
#         self.__tokens = []

#     def set_text(self, text):
#         self.__tokens = wordpunct_tokenize(text if text else '')
#         return self

#     def remove_accents(self):
#         text = self.get_text()
#         text = unicodedata.normalize(
#             'NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
#         self.set_text(text)
#         return self

#     def tokenize(self):
#         self.__tokens = wordpunct_tokenize(text if text else '')
#         return self

#     def standardize(self):
#         self.__tokens = [word.lower() for word in self.__tokens if (
#             word.isalnum() and not word.isnumeric())]
#         self.__tokens = [
#             word for word in self.__tokens if word not in self.__bad_list]
#         return self

#     def remove_stop_words(self):
#         self.__tokens = [word for word in self.__tokens
#                          if not word in self.__stopwords]
#         return self

#     def stemming(self):
#         self.__tokens = [self.__stemmer.stem(
#             word) for word in self.__tokens]
#         return self

#     def lemmatization(self):
#         self.__tokens = [tokens.lemma_ for tokens in self.__lemm(
#             ' '.join(word for word in self.__tokens))]
#         return self

#     def pipeline(self):
#         self.standardize().remove_stop_words().lemmatization()
#         return self

#     def stemming_pipeline(self):
#         self.standardize().remove_stop_words().stemming()
#         return self

#     def get_text(self):
#         return ' '.join(word for word in self.__tokens if word not in self.__bad_root)

#     def get_tokens(self):
#         return self.__tokens


