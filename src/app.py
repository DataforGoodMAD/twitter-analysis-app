import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from db_queries import DBQueries
from tw_miner import TwitterMiner
from tw_processor import TwitterProcessor

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
    users = queries.getFollowersNotReviewed()
    for user in users[0:3]:
        cursor = miner.followersCursor(
            screen_name=user.screen_name, limit=20)
        for user in cursor:
            # Check if user is active:
            if (datetime.now() - user.status.created_at) < timedelta(days=14) and user.statuses_count > 50 and user.default_profile_image == False:
                tweets = miner.api.user_timeline(
                    screen_name=user.screen_name, tweet_mode='extended', count=50)
            for tweet in tweets:
                if tweet.display_text_range != [0, 0]:
                    tweet_tokenized = " ".join(
                        processor.tweetTokenizer(tweet))
                    spacy_doc = processor.nlp.make_doc(tweet_tokenized)
                    tweet.similarity = round(mean([spacy_doc.similarity(
                        user_tweet) for user_tweet in processor.userRefDocs]), 3)
                else:
                    tweet.similarity = float(0)
            similar_tweets = [queries.tweetToDB(
                tweet) for tweet in tweets if tweet.similarity > 0.7]
            if len(similar_tweets) > 3:
                queries.session.add_all(similar_tweets)
                user.similarity = round(
                    mean([tweet.similarity for tweet in tweets]), 3)
                user_object = queries.userToDB(user)
                queries.session.add(user_object)
                queries.session.commit()


if __name__ == "__main__":
    processor = TwitterProcessor()
    queries = DBQueries()
    miner = TwitterMiner()

    updateTimeline(processor, queries, miner)
    updateTokensCount(processor, queries)
    updateFollowers(queries, miner, miner.username)
