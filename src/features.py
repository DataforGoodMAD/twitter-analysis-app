from statistics import mean

import tweepy
from dotenv import load_dotenv

from src.db_models import Base
from src.db_queries import DBQueries
from src.tw_miner import TwitterMiner
from src.tw_processor import TwitterProcessor
from src.settings import configCheck, firstTimeConfig

load_dotenv()


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
            processor.updatepopCounter(
                tokens_list * int(((tweet.retweet_count * 3) + tweet.favorite_count))
            )

    queries.session.commit()
    print("Update Timeline: Done")


def updateTokensCount(processor, queries):
    """Updates the tokens_count table with the latest tweets from the main user.

    Arguments:
        processor {[TwitterProcessor object]} -- [instance from the local class defined at tw_processor.py]
        queries {[DBQueries object]} -- [instance from the local class defined at tw_processor.py]
    """
    token_object_list = queries.tokenstoDB(processor.counter, processor.popCounter)
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


def updateFriends(queries, miner, target_user):

    stored_users = queries.listUsers()
    cursor = miner.friendsCursor(screen_name=target_user, limit=0)

    user_objects_list = []
    for user in cursor:
        if (user.id, user.screen_name) in stored_users:
            user = queries.getUser(user.id)
        user.is_friend = 1
        user.is_follower = 1 if user.id in miner.followersList else 0
        if isinstance(user, tweepy.models.User):
            user_object = queries.userToDB(user)
            user_objects_list.append(user_object)

    queries.session.add_all(user_objects_list)
    queries.session.commit()

    print("Update Friends: Done")


def secondGradeSearch(miner, processor, queries):
    not_reviewed_users = queries.getUsers(only_not_reviewed=True, only_followers=True)
    ref_docs = processor.toSpacyDocs(queries.getUserTweets(limit=50))

    for follower in not_reviewed_users:
        cursor = miner.followersCursor(screen_name=follower.screen_name, limit=0)
        reviewed_counter = 0
        if follower.followers_count >= 3200 and reviewed_counter == 0:
            follower.reviewed = 1
        while True:
            # TODO: intentar paralelizarlo con concurrent.futures:
            try:
                user = cursor.next()
                user = queries.checkSecondGradeUser(user)  # Check user on db
                if (
                    not user
                    or miner.reviewFriendFollower(user) == False  # Check with Twitter
                    or processor.isActive(user) == False  # Check activity
                ):
                    continue
                else:
                    # Request the last 50 tweets
                    tweets = miner.api.user_timeline(
                        screen_name=user.screen_name, tweet_mode="extended", count=50
                    )
                    similar_tweets = processor.similarityPipe(tweets, ref_docs)
                    user.similarity = round(
                        mean([tweet.similarity for tweet in tweets]), 3
                    )
                    # Check if user is a database object or must be created new.
                    if isinstance(user, tweepy.models.User):
                        user_object = queries.userToDB(user)
                        queries.session.add(user_object)
                        print(
                            f"User {user.screen_name} saved to database with similarity score {user.similarity}"
                        )

                    similar_tweets = [
                        queries.tweetToDB(tweet)
                        for tweet in similar_tweets
                        if not queries.checkTweetExist(tweet)
                    ]

                    queries.session.add_all(similar_tweets)

                # Commit Changes to database.
                queries.session.commit()

            except StopIteration:
                break

        follower.reviewed = 1
        reviewed_counter += 1

        print(f"Follower {follower.screen_name} reviewed.")
    queries.session.commit()
    print("Second Grade Search: Done")


if __name__ == "__main__":
    pass
