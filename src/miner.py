from typing import Any, Dict, List
import os
from .schemas import User, Token, Tweet
import tweepy

from src.log_config import logger
from .user_env import consumer_key, consumer_secret, username

# Connection to Twitter API
tweepy_auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
tweepy_client = tweepy.API(tweepy_auth)

async def countHandler(limit):
    if limit == 0 or limit > 200:
        count = 200
    else:
        count = limit
    return count


async def timeline_cursor(
    username, include_rts=False, exclude_replies=True, limit=200, since_id=None
):

    count = await countHandler(limit)
    logger.info(f"since_id = {since_id}")
    print(f"since_id = {since_id}")
    return tweepy.Cursor(
        tweepy_client.user_timeline,
        screen_name=username,
        tweet_mode="extended",
        since_id=since_id,
        include_rts=include_rts,
        exclude_replies=exclude_replies,
        count=count,
    ).items(limit)


async def followers_cursor(screen_name, limit=200):
    count = await countHandler(limit)
    return tweepy.Cursor(
        tweepy_client.followers,
        id=screen_name,
        count=count,
    ).items(limit)

async def friends_cursor(screen_name, limit=200):
    count = await countHandler(limit)
    return tweepy.Cursor(
        tweepy_client.friends,
        id=screen_name,
        count=count,
    ).items(limit)

    # TODO
    # if screen_name == self.username:
    #     return cursor
    # else:
    #     user_reviewed = self.db.checkUserReviewed(screen_name)
    #     if user_reviewed:
    #         print(f"User {screen_name} already reviewed.")
    #         return []
    #     return cursor

async def get_users_from_twitter(usernames):
    return tweepy_client.lookup_users(screen_names=usernames)

async def twitter_followers_list(screen_name):
    return tweepy_client.followers_ids(screen_name=screen_name)

async def twitter_friends_list(screen_name):
    return tweepy_client.friends_ids(screen_name=screen_name)


class TwitterMiner:
    def __init__(self):

        # Main User
        self.username = os.getenv("USER_SCREEN_NAME")

        # Connection to Twitter API
        self.consumer_key = os.environ.get("CONSUMER_KEY")
        self.consumer_secret = os.environ.get("CONSUMER_SECRET_KEY")
        self.auth = tweepy.AppAuthHandler(self.consumer_key, self.consumer_secret)
        self.api = tweepy.API(self.auth)

        # API request. List of users followed by the main account.
        self.friendsList = self.api.friends_ids(screen_name=self.username)
        # API request. List of main account's followers.
        self.followersList = self.api.followers_ids(screen_name=self.username)

        # DB Connection
        self.db = DB()

    def friendsCursor(self, screen_name, limit=200):
        count = self.countHandler(limit)

        cursor = tweepy.Cursor(self.api.friends, id=screen_name, count=count).items(
            limit
        )

        if screen_name == self.username:
            return cursor

        else:
            user_reviewed = self.db.checkUserReviewed(screen_name)
            if user_reviewed:
                print(f"User {screen_name} already reviewed.")
                return []
            return cursor

    def updateFriendsList(self):
        self.friendsList = self.api.friends_ids(screen_name=self.username)
        return self.friendsList

    def updateFollowersList(self):
        self.followersList = self.api.followers_ids(screen_name=self.username)
        return self.followersList

    def searchCursor(self, query, result_type="recent", limit=200):
        count = self.countHandler(limit)
        return tweepy.Cursor(
            self.api.search, q=query, result_type=result_type, count=count
        ).items(limit)

    def reviewFriendFollower(self, user):
        user.is_friend = 1 if user.id in self.friendsList else 0
        user.is_follower = 1 if user.id in self.followersList else 0
        return True if user.is_friend == 0 and user.is_follower == 0 else False


if __name__ == "__main__":
    m = TwitterMiner()
    m.username
    print(m.api.user_timeline(screen_name=m.username, tweet_mode="extended"))
