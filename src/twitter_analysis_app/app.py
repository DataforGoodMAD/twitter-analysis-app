from statistics import mean

import tweepy

from .db_queries import DBQueries
from .tw_miner import TwitterMiner
from .tw_processor import TwitterProcessor


class TwitterAnalysisFeatures():
    def __init__(self) -> None:
        self.db = DBQueries()
        self.miner = TwitterMiner()
        self.processor = TwitterProcessor()

    def update_timeline(self):
        cursor = self.miner.timelineCursor(
            username=self.miner.username, limit=0)

        for tweet in cursor:
            tweet_object = self.db.tweetToDB(tweet)
            if tweet_object:
                self.db.session.add(tweet_object)
                tokens_list = self.processor.tweetTokenizer(tweet.full_text)
                self.processor.updateCounter(tokens_list)
                self.processor.updatepopCounter(
                    tokens_list *
                    int(((tweet.retweet_count * 3) + tweet.favorite_count))
                )

        self.db.session.commit()
        print("Update Timeline: Done")

    def update_tokens_count(self):
        token_object_list = self.db.tokenstoDB(
            self.processor.counter, self.processor.popCounter)
        self.db.session.add_all(token_object_list)
        self.db.session.commit()
        print("Update Tokens: Done")

    def update_followers(self, target_user):

        stored_users = self.db.listUsers()
        cursor = self.miner.followersCursor(screen_name=target_user, limit=0)

        user_objects_list = []
        for user in cursor:
            if (user.id,) in stored_users:
                break
            else:
                user.is_friend = 1 if user.id in self.miner.friendsList else 0
                user.is_follower = 1 if user.id in self.miner.followersList else 0
                user_object = self.db.userToDB(user)
                user_objects_list.append(user_object)

        self.db.session.add_all(user_objects_list)
        self.db.session.commit()

        print("Update Followers: Done")

    def update_friends(self, target_user):

        stored_users = self.db.listUsers()
        cursor = self.miner.friendsCursor(screen_name=target_user, limit=0)

        user_objects_list = []
        for user in cursor:
            if (user.id,) in stored_users:
                user = self.db.getUser(user.id)
            user.is_friend = 1
            user.is_follower = 1 if user.id in self.miner.followersList else 0
            if isinstance(user, tweepy.models.User):
                user_object = self.db.userToDB(user)
                user_objects_list.append(user_object)

        self.db.session.add_all(user_objects_list)
        self.db.session.commit()

        print("Update Friends: Done")

    def second_grade_search(self):
        not_reviewed_users = self.db.getUsers(
            only_not_reviewed=True, only_followers=True)
        ref_docs = self.processor.toSpacyDocs(
            self.db.getUserTweets(limit=50))

        for follower in not_reviewed_users:
            cursor = self.miner.followersCursor(
                screen_name=follower.screen_name, limit=0)
            reviewed_counter = 0
            if follower.followers_count >= 3200 and reviewed_counter == 0:
                follower.reviewed = 1
            while True:
                # TODO: intentar paralelizarlo con concurrent.futures:
                try:
                    user = cursor.next()
                    user = self.db.checkSecondGradeUser(
                        user)  # Check user on db
                    if (
                        not user
                        # Check with Twitter
                        or self.miner.reviewFriendFollower(user) == False
                        # Check activity
                        or self.processor.isActive(user) == False
                    ):
                        continue
                    else:
                        # Request the last 50 tweets
                        tweets = self.miner.api.user_timeline(
                            screen_name=user.screen_name, tweet_mode="extended", count=50
                        )
                        similar_tweets = self.processor.similarityPipe(
                            tweets, ref_docs)
                        user.similarity = round(
                            mean([tweet.similarity for tweet in tweets]), 3
                        )
                        # Check if user is a database object or must be created new.
                        if isinstance(user, tweepy.models.User):
                            user_object = self.db.userToDB(user)
                            self.db.session.add(user_object)
                            print(
                                f"User {user.screen_name} saved to database with similarity score {user.similarity}"
                            )

                        similar_tweets = [
                            self.db.tweetToDB(tweet)
                            for tweet in similar_tweets
                            if not self.db.checkTweetExist(tweet)
                        ]

                        self.db.session.add_all(similar_tweets)

                    # Commit Changes to database.
                    self.db.session.commit()

                except StopIteration:
                    break

            follower.reviewed = 1
            reviewed_counter += 1

            print(f"Follower {follower.screen_name} reviewed.")
        self.db.session.commit()
        print("Second Grade Search: Done")
