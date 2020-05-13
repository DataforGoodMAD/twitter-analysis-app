import logging
import os

import tweepy
from dotenv import load_dotenv

from db_queries import DBQueries

load_dotenv()


class TwitterMiner:

    def __init__(self):

        # Main User
        self.username = os.getenv('username')

        # Connection to Twitter API
        self.consumer_key = os.environ.get('CONSUMER_KEY')
        self.consumer_secret = os.environ.get('CONSUMER_SECRET_KEY')
        self.auth = tweepy.AppAuthHandler(
            self.consumer_key, self.consumer_secret)
        self.api = tweepy.API(
            self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        # DB Connection
        self.db_queries = DBQueries()

    def limitHandler(Self, limit):
        if limit == 0 or limit > 200:
            count = 200
        else:
            count = limit
        logging.info(f'limit = {limit}, count = {count}')
        return limit, count

    # TODO: Decorator for 403 error: forbiddenRequestHandler
    def forbiddenRequestHandler():
        pass

    def timelineCursor(self, username, include_rts=False, exclude_replies=True, limit=200, since_id=None):
        """
        Set limit to 0 to try to retrieve the full timeline.
        This method returns a cursor, but you have to iterate over it to make the requests.
        """

        if limit == 0 or limit > 200:
            count = 200
        else:
            count = limit
        logging.info(f'limit = {limit}, count = {count}')

        if not since_id:
            since_id = self.db_queries.topTweetId()
            if since_id:
                since_id = since_id[0]
        logging.info(f'since_id = {since_id}')
        print(f'since_id = {since_id}')
        return tweepy.Cursor(self.api.user_timeline,
                             id=username,
                             tweet_mode='extended',
                             since_id=since_id,
                             include_rts=include_rts,
                             exclude_replies=exclude_replies,
                             count=count).items(limit)

    def followersCursor(self, screen_name):

        limit, count = self.limitHandler(limit)

        return tweepy.Cursor(api.followers,
                             id=screen_name,

                             count=count).items(limit)


if __name__ == "__main__":
    pass
