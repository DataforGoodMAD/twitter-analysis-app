from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN, INTEGER, VARCHAR, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./twitterdb.db", echo=True)
Base = declarative_base(bind=engine)


class AccountTimeline(Base):

    __tablename__ = "account_timeline"

    tweet_id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER)
    created_at = Column(DATETIME)
    full_text = Column(VARCHAR(300))
    hashtags = Column(VARCHAR(300))
    truncated = Column(INTEGER)
    display_text_range = Column(VARCHAR(100))
    retweet_count = Column(INTEGER)
    favorite_count = Column(INTEGER)


class TokensCount(Base):

    __tablename__ = "tokens_count"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    token = Column(VARCHAR(300))
    cumulated_count = Column(INTEGER)
    popularity_count = Column(INTEGER)
    is_hashtag = Column(BOOLEAN)
    last_updated = Column(DATETIME)


class User(Base):

    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True)
    screen_name = Column(VARCHAR(200))
    location = Column(VARCHAR(200))
    protected = Column(BOOLEAN)
    followers_count = Column(INTEGER)
    friends_count = Column(INTEGER)
    created_at = Column(DATETIME)
    favourites_count = Column(INTEGER)
    statuses_count = Column(INTEGER)
    default_profile_image = Column(BOOLEAN)
    is_follower = Column(BOOLEAN, nullable=True)
    is_friend = Column(BOOLEAN, nullable=True)
    last_status = Column(DATETIME, nullable=True)
    reviewed = Column(BOOLEAN)
    similarity_score = Column(FLOAT, nullable=True)
    tweets = relationship("Tweet", back_populates="user")


class Tweet(Base):

    __tablename__ = "tweets"

    tweet_id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey("users.id"))
    created_at = Column(DATETIME)
    full_text = Column(VARCHAR(300))
    hashtags = Column(VARCHAR(300))
    truncated = Column(INTEGER)
    display_text_range = Column(VARCHAR(100))
    retweet_count = Column(INTEGER)
    favorite_count = Column(INTEGER)
    similarity_score = Column(FLOAT, nullable=True)
    user = relationship("User", back_populates="tweets")
