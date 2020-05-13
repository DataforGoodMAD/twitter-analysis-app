import os
import logging
from dotenv import load_dotenv

from tw_miner import TwitterMiner
from tw_processor import TwitterProcessor
from db_queries import DBQueries

load_dotenv()

logger = logging.getLogger('log')


def updateTimeline(processor, queries, miner):
    """Updates the account_timeline table with the latest tweets from the main user.

    Arguments:
        processor {[TwitterProcessor instance]}
        queries {[DBQueries instance]}
        cursor {[Tweepy Cursor instance]}
    """

    cursor = miner.timelineCursor(username=miner.username, limit=0)

    for tweet in cursor:
        tweet_object = queries.tweetToDB(tweet)
        if tweet_object:
            queries.session.add(tweet_object)
            tokens_list = processor.tweetTokenizer(tweet.full_text)
            processor.updateCounter(tokens_list)
            print(f'tweet: {tweet.id}, processed')

    queries.session.commit()
    print("Session Commited")


def updateTokensCount(processor, queries):
    """Updates the tokens_count table with the latest tweets from the main user.

    Arguments:
        processor {[type]} -- [description]
        queries {[type]} -- [description]
    """
    token_object_list = queries.tokenstoDB(processor.counter)
    queries.session.add_all(token_object_list)
    queries.session.commit()
    print("Session Commited")


def updateFollowers(queries, miner):

    stored_users = queries.listUserIds()
    cursor = miner.followersCursor(screen_name=miner.username, limit=0)
    user_objects_list = []
    for page in cursor:

        for user in page:
            user_object = queries.userToDB(user)
        user_objects_list.append(user_object)

        if page[-1].id in stored_users:
            break

    queries.session.add_all(user_objects_list)
    queries.session.commit()
    print("Session Commited")


if __name__ == "__main__":
    processor = TwitterProcessor()
    queries = DBQueries()
    miner = TwitterMiner()

    updateTimeline(processor, queries, miner)
    updateTokensCount(processor, queries)
    updateFollowers(queries, miner)
