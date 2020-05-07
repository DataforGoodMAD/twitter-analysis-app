import os
import logging
import tweepy
from sqlalchemy import func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from database_setup import AccountTimeline, User, Tweet
from dotenv import load_dotenv

load_dotenv()

class TwitterMiner:

    def __init__(self, username):

        #Main User
        self.username = username

        #Connection to Twitter API
        self.consumer_key = os.environ.get('CONSUMER_KEY')
        self.consumer_secret = os.environ.get('CONSUMER_SECRET_KEY')
        self.auth = tweepy.AppAuthHandler(self.consumer_key, self.consumer_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
        #Connection to Database
        self.engine = create_engine('sqlite:///./twitterdb.db', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def __repr__(self):
        return f'TwitterMiner Instance. Connected to API: {self.api} and Database: {self.engine}'



    def postTweetToDatabase(self, cursor):
        """
        Status is the tweet object returned by Tweepy.
        """

        for status in cursor:
            try:
                params = {
                    'tweet_id' : status.id,
                    'user_id' : status.author.id,
                    'created_at' : status.created_at,
                    'full_text' : status.full_text,
                    'truncated' : status.truncated,
                    'display_text_range' : str(status.display_text_range),
                    'retweet_count' : status.retweet_count,
                    'favorite_count' : status.favorite_count,
                    'possibly_sensitive' : status.possibly_sensitive,
                }

                if status.author.screen_name == self.username:
                    tweet = AccountTimeline(**params)
                else:
                    tweet = Tweet(**params)

                self.session.add(tweet)

            except Exception as e:
                logging.error(e)
        
        self.session.commit()




    def timelineCursorRequest(self, user_id, include_rts=False, exclude_replies=True, limit=200, since_id=None):
        """
        Set limit to None to try to retrieve the full timeline.
        This method returns a cursor, but you have to iterate over it to make the requests.
        """

        if not limit or limit > 200:
            counter = 200
        else:
            counter = limit
        logging.info(f'limit = {limit}, counter = {counter}')

        if not since_id:
            since_id = self.session.query(func.max(AccountTimeline.tweet_id)).one()
            if since_id:
                since_id = since_id[0]
        logging.info(f'since_id = {since_id}')
        print(f'since_id = {since_id}')
        return tweepy.Cursor(self.api.user_timeline,
                             id=user_id,
                             tweet_mode='extended',
                             since_id=since_id,
                             include_rts=include_rts,
                             exclude_replies=exclude_replies,
                             count=counter).items(limit)

if __name__ == "__main__":
    miner = TwitterMiner(username='helsinkiespana')
    cursor = miner.timelineCursorRequest(user_id=miner.username, limit=2)
    miner.postTweetToDatabase(cursor)