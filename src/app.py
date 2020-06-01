import logging
import os
import sys
import warnings
from statistics import mean

import tweepy
from dotenv import load_dotenv

from db_queries import DBQueries
from tw_miner import TwitterMiner
from tw_processor import TwitterProcessor

load_dotenv()

# Disable warnings for production. Change PYTHONWARNINGS to 'default' to debug.
python_warnings = os.getenv('PYTHONWARNINGS')
warnings.simplefilter(python_warnings)


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
    cursor = miner.followersCursor(screen_name=target_user, limit=0)

    user_objects_list = []
    for user in cursor:
        if (user.id, user.screen_name) in stored_users:
            break
        else:
            user.is_friend = 1 if user.id in miner.friendsList else 0
            user.is_follower = 1 if user.id in miner.followersList else 0
            user_object = queries.userToDB(user)
            user_objects_list.append(user_object)

    queries.session.add_all(user_objects_list)
    queries.session.commit()

    print("Update Followers: Done")


def secondGradeSearch(miner, processor, queries):
    not_reviewed_users = queries.getFollowers(only_not_reviewed=True)
    ref_docs = processor.toSpacyDocs(
        queries.getUserTweets(limit=50))  # Main Account Docs
    for follower in not_reviewed_users[0:3]:
        cursor = miner.followersCursor(
            screen_name=follower.screen_name, limit=20)
        while True:
            try:
                user = next(cursor)
            except StopIteration:
                break

            # Check the user on the database, and looks for is_follower is_friend and similarity_score.
            user_db = queries.checkSecondGradeUser(user.id)
            if user_db:
                user = user_db
            ff = miner.updateFriendFollower(user)
            if ff == (0, 0) and processor.isActive(user):
                # Request the last 50 tweets
                tweets = miner.api.user_timeline(
                    screen_name=user.screen_name, tweet_mode='extended', count=50)

                similar_tweets = processor.similarityPipe(tweets, ref_docs)
                user.similarity = round(
                    mean([tweet.similarity for tweet in tweets]), 3)
                # Check if user is a database object or must be created new.
                if isinstance(user, tweepy.models.User):
                    user_object = queries.userToDB(user)
                    queries.session.add(user_object)

                similar_tweets = [queries.tweetToDB(
                    tweet) for tweet in similar_tweets if not queries.checkTweetExist(tweet)]

                queries.session.add_all(similar_tweets)

            # Commit Changes to database.
            queries.session.commit()

        follower.reviewed = 1
    queries.session.commit()
    print('Second Grade Search: Done')


def main():
    processor = TwitterProcessor()
    print("TwitterProcessor instance created")
    queries = DBQueries()
    print("DBQueries instance created")
    miner = TwitterMiner()
    print("TwitterMiner instance created")

    updateTimeline(processor, queries, miner)
    updateTokensCount(processor, queries)
    updateFollowers(queries, miner, miner.username)
    secondGradeSearch(miner, processor, queries)


if __name__ == "__main__":
    main()
