import logging

from sqlalchemy import Column, ForeignKey, INTEGER, VARCHAR, DATETIME
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN, INTEGER, VARCHAR 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite:///./twitterdb.db', echo=True)


class AccountTimeline(Base):

    __tablename__ = 'account_timeline'

    tweet_id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER)
    created_at = Column(DATETIME)
    full_text = Column(VARCHAR(300))
    truncated = Column(INTEGER)
    display_text_range = Column(VARCHAR(100))
    retweet_count = Column(INTEGER)
    favorite_count = Column(INTEGER)
    possibly_sensitive = Column(BOOLEAN)


class User(Base):

    __tablename__ = 'users'

    user_id = Column(INTEGER, primary_key=True)
    screen_name = Column(VARCHAR(200))
    location = Column(VARCHAR(200))
    protected = Column(BOOLEAN)
    followers_count = Column(INTEGER)
    friends_count = Column(INTEGER)
    created_at = Column(DATETIME)
    favourites_count = Column(INTEGER)
    statuses_count = Column(INTEGER)
    lang = Column(VARCHAR(100))
    default_profile_image = Column(BOOLEAN)
    is_follower = Column(BOOLEAN)
    is_friend = Column(BOOLEAN)
    status = Column(INTEGER)


class Tweet(Base):

    __tablename__ = 'tweets'

    tweet_id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('users.user_id'))
    created_at = Column(DATETIME)
    full_text = Column(VARCHAR(300))
    truncated = Column(BOOLEAN)
    display_text_range = Column(VARCHAR(100))
    retweet_count = Column(INTEGER)
    favorite_count = Column(INTEGER)
    possibly_sensitive = Column(BOOLEAN)

    user = relationship("User", back_populates="tweets")


User.tweets = relationship(
    'Tweet', order_by=Tweet.tweet_id, back_populates="user")


if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        logging.info("Tables created")
    except Exception as e:
        logging.error(e)