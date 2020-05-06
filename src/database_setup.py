from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite:///twitterdb.db')

Base.metadata.create_all(engine)

class UserTimeline(Base):
    __tablename__ = 'user_timeline'

    id_ = Column(Integer, primary_key=True)
    created_at = Column(Integer, primary_key=True)
    id
    full_text
    truncated
    display_text_range
    retweet_count
    favorite_count
    favorited
    retweeted
    possibly_sensitive

   title = Column(String(250), nullable=False)
   author = Column(String(250), nullable=False)
   genre = Column(String(250))


