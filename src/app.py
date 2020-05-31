import logging
import os
from datetime import datetime, timedelta
from statistics import mean

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
    all_users = queries.getFollowers()
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
            # Check if user is active:
            if hasattr(user, 'status') and (datetime.now() - user.status.created_at) < timedelta(days=14) and user.statuses_count > 50 and user.default_profile_image == False:
                # Request the last 50 tweets
                tweets = miner.api.user_timeline(
                    screen_name=user.screen_name, tweet_mode='extended', count=50)
                # Compare similarity of each tweet with the main account ref_docs:
                for tweet in tweets:
                    tweet_tokenized = " ".join(
                        processor.tweetTokenizer(tweet.full_text))
                    spacy_doc = processor.nlp.make_doc(tweet_tokenized)
                    tweet.similarity = round(mean([spacy_doc.similarity(
                        user_tweet) for user_tweet in ref_docs]), 3)
                # TODO: Chequear si el tweet está en la base de datos antes de intentar guardarlo
                similar_tweets = [queries.tweetToDB(
                    tweet) for tweet in tweets if tweet.similarity > 0.7]

                if len(similar_tweets) > 3:
                    # Check whether the user is already in our database, and if so, update it:
                    existent_user = [
                        u for u in all_users if u.user_id == user.id]
                    if existent_user:
                        user = existent_user[0]
                        user.is_friend = 1 if user.user_id in miner.friendsList else 0
                        user.is_follower = 1 if user.user_id in miner.followersList else 0
                        user.similarity = round(
                            mean([tweet.similarity for tweet in tweets]), 3)

                    else:
                        # User for Database
                        user.is_friend = 1 if user.id in miner.friendsList else 0
                        user.is_follower = 1 if user.id in miner.followersList else 0
                        user.similarity = round(
                            mean([tweet.similarity for tweet in tweets]), 3)
                        user_object = queries.userToDB(user)
                        queries.session.add(user_object)
                    # Tweets for Database
                    queries.session.add_all(similar_tweets)
                    user_object = queries.userToDB(user)
                    queries.session.commit()
        follower.reviewed = 1
    queries.session.commit()
    print('Second Grade Search: Done')


if __name__ == "__main__":
    processor = TwitterProcessor()
    print("TwitterProcessor instance created")
    queries = DBQueries()
    print("DBQueries instance created")
    miner = TwitterMiner()
    print("TwitterMiner instance created")

    updateTimeline(processor, queries, miner)
    updateTokensCount(processor, queries)
    updateFollowers(queries, miner, miner.username)
    #secondGradeSearch(miner, processor, queries)
