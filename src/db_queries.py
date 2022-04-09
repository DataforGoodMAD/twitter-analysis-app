from contextlib import contextmanager
from datetime import datetime
from datetime import datetime
import csv
import os
import re

from dotenv import load_dotenv

from sqlalchemy import create_engine, func
from sqlalchemy.orm import relationship, sessionmaker

from src.db_models import Base, AccountTimeline, TokensCount, Tweet, User
from src.log_config import logger

load_dotenv()


class DBQueries:
    def __init__(self):

        self.username = os.getenv("USER_SCREEN_NAME")

        # Connection to Database
        self.engine = create_engine("sqlite:///./twitterdb.db", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()
        self._base = Base

    def create_tables(self):
        logger.info(self._base.metadata.create_all())
        print("Database Loaded.")

    @contextmanager
    def get_session(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def topTweetId(self):
        return self.session.query(func.max(AccountTimeline.tweet_id)).one()

    def tweetToDB(self, status):
        """Map a Status object from Tweepy to a tweet object for the database model.
        This method identifies whether the tweets came from the main user, or from other accounts

        Arguments:
            status {[Tweepy Status object]} -- [Status is the tweet object returned by Tweepy.]

        Returns:
            [sqlalchemy object] -- [Depending on tweet's author, the object will be from Tweets or AccountTimeline.]
        """

        try:
            params = {
                "tweet_id": status.id,
                "user_id": status.author.id,
                "created_at": status.created_at,
                "full_text": status.full_text,
                "hashtags": str(
                    list(
                        map(
                            lambda hashtag: hashtag["text"],
                            status._json.get("entities", None).get(
                                "hashtags", None
                            ),
                        )
                    )
                ),
                "truncated": status.truncated,
                "display_text_range": str(status.display_text_range),
                "retweet_count": status.retweet_count,
                "favorite_count": status.favorite_count,
            }

            if status.author.screen_name == self.username:
                tweet_object = AccountTimeline(**params)
            else:
                params["similarity_score"] = (
                    status.similarity
                    if hasattr(status, "similarity")
                    else None
                )
                tweet_object = Tweet(**params)

            return tweet_object

        except Exception:
            logger.exception("Exception occurred")

    def tokenstoDB(self, counter, popCounter):
        """Transforms a Counter object to a list of objects of the TokensCount model.

        Arguments:
            counter {Counter} -- [Counter from collections with tokens as keys and the ocurrences of each one on a set of tweets as value.]
        """
        keys = counter.elements()  # List of Tokens

        tokens_query = (
            self.session.query(TokensCount)
            .filter(TokensCount.token.in_(keys))
            .all()
        )

        for token_object in tokens_query:
            if token_object.token in keys:
                token_object.cumulated_count += counter.get(token_object.token)
                token_object.popularity_count += popCounter.get(
                    token_object.token
                )
                token_object.last_updated = datetime.now()
                del counter[token_object.token]

        token_object_list = []
        for count, pop_count in zip(counter.items(), popCounter.items()):
            token = count[0]
            value = count[1]
            pop_value = pop_count[1]
            if len(token) > 2:
                token_object = TokensCount(
                    token=token,
                    cumulated_count=value,
                    popularity_count=pop_value,
                    is_hashtag=True if re.match(r"^#", token) else False,
                    last_updated=datetime.now(),
                )
                token_object_list.append(token_object)
        return token_object_list

    def userToDB(self, user):
        try:
            params = {
                "id": user.id,
                "screen_name": user.screen_name,
                "location": user.location,
                "protected": user.protected,
                "followers_count": user.followers_count,
                "friends_count": user.friends_count,
                "created_at": user.created_at,
                "favourites_count": user.favourites_count,
                "statuses_count": user.statuses_count,
                "default_profile_image": user.default_profile_image,
                "is_follower": user.is_follower,
                "is_friend": user.is_friend,
                "last_status": (
                    user.status.created_at if hasattr(user, "status") else None
                ),
                "reviewed": 0,
                "hidden": 0,
                "similarity_score": (
                    user.similarity if hasattr(user, "similarity") else None
                ),
            }

            user_object = User(**params)
            return user_object

        except Exception as e:
            print(e)

    def getUsers(
        self, only_not_reviewed=False, only_followers=False, only_friends=False
    ):
        query = "self.session.query(User)"
        if only_not_reviewed:
            query += ".filter(User.reviewed == False)"
        if only_followers:
            query += ".filter(User.is_follower == True)"
        if only_friends:
            query += ".filter(User.is_friend == True)"
        query += ".all()"
        return eval(query)

    def getUserTweets(
        self,
        limit=50,
        order_by=AccountTimeline.created_at.desc(),
        with_text=True,
    ):
        if with_text:
            return (
                self.session.query(AccountTimeline.full_text)
                .filter(AccountTimeline.display_text_range != "[0,0]")
                .order_by(order_by)
                .limit(limit)
                .all()
            )
        return (
            self.session.query(AccountTimeline.full_text)
            .order_by(order_by)
            .limit(limit)
            .all()
        )

    def checkUserReviewed(self, screen_name):
        """Check whether the user has been marked as reviewed in the database.

        Arguments:
            screen_name {[string]} -- [User screen_name to check]

        Returns:
            [bool] -- [True if has been already reviewed]
        """
        return (
            self.session.query(User.reviewed)
            .filter(User.screen_name == screen_name)
            .first()[0]
        )

    def listUsers(self):
        return self.session.query(User.id).all()

    def checkSecondGradeUser(self, user_tweepy):
        user_db = self.session.query(User).filter_by(id=user_tweepy.id).first()
        if (
            user_db
            and user_db.is_follower == 0
            and user_db.is_friend == 0
            and user_db.similarity_score is None
        ):
            return user_db
        elif user_db:
            return None
        else:
            return user_tweepy

    def checkTweetExist(self, tweet):
        q = self.session.query(Tweet).filter_by(tweet_id=tweet.id)
        return self.session.query(q.exists()).scalar()

    def getUser(self, user_id):
        return self.session.query(User).filter_by(id=user_id).first()

    def get_similar_users(self, hidden=False):
        with self.get_session() as session:
            sim_users = (
                session.query(User)
                .filter(User.similarity_score >= 0.75, User.hidden == hidden)
                .order_by(
                    User.similarity_score.desc(),
                )
                .all()
            )
        data = [
            [
                user.screen_name,
                user.followers_count,
                user.statuses_count,
                datetime.strftime(user.last_status, "%d/%m/%y"),
                user.similarity_score,
            ]
            for user in sim_users
        ]
        return data

    def _export_table_to_csv(self, table):
        with open(f"./{table.__tablename__}.csv", "w") as file:
            records = self.session.query(table).all()
            csv_writer = csv.writer(file, delimiter=",")
            output = [
                csv_writer.writerow(
                    [
                        getattr(curr, column.name)
                        for column in table.__mapper__.columns
                    ]
                )
                for curr in records
            ]

    @property
    def tables(self):
        # FIXME: get models dinamically
        return [AccountTimeline, TokensCount, Tweet, User]
