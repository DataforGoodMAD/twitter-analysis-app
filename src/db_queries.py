import logging
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, func
from sqlalchemy.orm import relationship, sessionmaker

from db_models import AccountTimeline, TokensCount, Tweet, User

load_dotenv()


class DBQueries:
    def __init__(self):

        self.username = os.getenv('username')

        # Connection to Database
        self.engine = create_engine('sqlite:///./twitterdb.db', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def topTweetId(self):
        return self.session.query(
            func.max(AccountTimeline.tweet_id)).one()

    def tweetToDB(self, status):
        """Map a Status object from Tweepy to a tweet object for the database model. 
        This method identifies whether the tweets came from the main user, or from other accounts

        Arguments:
            status {[Tweepy Status object]} -- [Status is the tweet object returned by Tweepy.]

        Returns:
            [sqlalchemy object] -- [Depending on tweet's author, the object will be from Tweets or AccountTimeline.]
        """

        try:
            params = {
                'tweet_id': status.id,
                'user_id': status.author.id,
                'created_at': status.created_at,
                'full_text': status.full_text,
                'hashtags': str(list(map(lambda hashtag: hashtag['text'], status._json.get('entities', None).get('hashtags', None)))),
                'truncated': status.truncated,
                'display_text_range': str(status.display_text_range),
                'retweet_count': status.retweet_count,
                'favorite_count': status.favorite_count,
            }

            if status.author.screen_name == self.username:
                tweet_object = AccountTimeline(**params)
            else:
                tweet_object = Tweet(**params)

            return tweet_object

        except Exception as e:
            logging.error(e)

    def tokenstoDB(self, counter):
        """Transforms a Counter object to a list of objects of the TokensCount model.

        Arguments:
            counter {[type]} -- [description]
        """
        existent_tokens = self.session.query(TokensCount.token).all()
        token_object_list = []
        for token, value in counter.items():
            if token in existent_tokens:
                token_object = TokensCount(
                    token=token,
                    cumulated_count=value,
                    is_hashtag=True if re.match(r'^#', token) else False,
                    last_updated=datetime.now()
                )
            else:
                token_object = TokensCount(
                    token=token,
                    cumulated_count=value,
                    is_hashtag=True if re.match(r'^#', token) else False,
                    last_updated=datetime.now()
                )
            token_object_list.append(token_object)
        return token_object_list


if __name__ == "__main__":
    pass
