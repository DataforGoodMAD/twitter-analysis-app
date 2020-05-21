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
            counter {Counter} -- [Counter from collections with tokens as keys and the ocurrences of each one on a set of tweets as value.]
        """
        keys = counter.elements()  # List of Tokens

        tokens_query = self.session.query(TokensCount).filter(
            TokensCount.token.in_(keys)).all()

        for token_object in tokens_query:
            if token_object.token in keys:
                token_object.cumulated_count += counter.get(token_object.token)
                token_object.last_updated = datetime.now()
                del counter[token_object.token]

        token_object_list = []
        for token, value in counter.items():
            if len(token) > 2:
                token_object = TokensCount(
                    token=token,
                    cumulated_count=value,
                    is_hashtag=True if re.match(r'^#', token) else False,
                    last_updated=datetime.now()
                )
                token_object_list.append(token_object)
        return token_object_list

    def userToDB(self, user):
        # TODO: Revisar como conseguir el "is_friend" en el endpoint de "friendships". Ver como actualizar el reviewed.

        try:
            params = {
                'user_id': user.id,
                'screen_name': user.screen_name,
                'location': user.location,
                'protected': user.protected,
                'followers_count': user.followers_count,
                'friends_count': user.friends_count,
                'created_at': user.created_at,
                'favourites_count': user.favourites_count,
                'statuses_count': user.statuses_count,
                'lang': user.lang,
                'default_profile_image': user.default_profile_image,
                'is_follower': user.is_follower,
                'is_friend': user.is_friend,
                'last_status': (user.status.created_at if hasattr(user, 'status') else None),
                'reviewed': 0
            }

            user_object = User(**params)
            return user_object

        except Exception as e:
            print(e)

    def getTopTokens(self):
        pass

    def checkUserReviewed(self, screen_name):
        """Check whether the user has been marked as reviewed in the database.

        Arguments:
            screen_name {[string]} -- [User screen_name to check]

        Returns:
            [bool] -- [True if has been already reviewed]
        """
        return self.session.query(User.screen_name).filter(User.reviewed == True)

    def listUsers(self):
        return self.session.query(User.user_id, User.screen_name).all()


if __name__ == "__main__":
    pass
