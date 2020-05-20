import os
import logging
from dotenv import load_dotenv

from tw_miner import TwitterMiner
from tw_processor import TwitterProcessor
from db_queries import DBQueries

from itertools import takewhile

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
    print("Update Timeline: Done")


def updateTokensCount(processor, queries):
    """Updates the tokens_count table with the latest tweets from the main user.

    Arguments:
        processor {[type]} -- [description]
        queries {[type]} -- [description]
    """
    token_object_list = queries.tokenstoDB(processor.counter)
    queries.session.add_all(token_object_list)
    queries.session.commit()
    print("Update Tokens: Done")


def updateFollowers(queries, miner, target_user):

    stored_users = queries.listUsers()
    cursor = miner.followersCursor(screen_name=target_user, limit=200)

    # user_objects_list = [queries.userToDB(user) for user in takewhile(
    #     lambda u: (u.id, u.screen_name) not in stored_users, cursor)]

    user_objects_list = []
    for user in cursor:
        if (user.id, user.screen_name) in stored_users:
            break
        else:
            user.is_friend = 1 if user.id in miner.friendsList else 0
            user.is_follower = 1 if target_user == miner.username else 0
            user_object = queries.userToDB(user)
            user_objects_list.append(user_object)

    queries.session.add_all(user_objects_list)
    queries.session.commit()
    print("Update Followers: Done")


if __name__ == "__main__":
    processor = TwitterProcessor()
    queries = DBQueries()
    miner = TwitterMiner()

    updateTimeline(processor, queries, miner)
    updateTokensCount(processor, queries)
    updateFollowers(queries, miner, miner.username)
