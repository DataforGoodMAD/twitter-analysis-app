from sqlalchemy import MetaData, Table
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.sqlite import DATETIME, BOOLEAN, INTEGER, VARCHAR, FLOAT

metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", INTEGER, primary_key=True),
    Column("screen_name", VARCHAR(200)),
    Column("location", VARCHAR(200)),
    Column("protected", BOOLEAN),
    Column("followers_count", INTEGER),
    Column("friends_count", INTEGER),
    Column("created_at", DATETIME),
    # Column("favourites_count", INTEGER),
    Column("statuses_count", INTEGER),
    Column("is_friend", BOOLEAN, nullable=True),
    Column("is_follower", BOOLEAN, nullable=True),
    Column("last_status", DATETIME, nullable=True),
    Column("reviewed", BOOLEAN),
    Column("similarity_score", FLOAT, nullable=True),
)

tweets_table= Table(
    "tweets",
    metadata,
    Column("tweet_id", INTEGER, primary_key=True),
    Column("user_id", INTEGER, ForeignKey("users.id")),
    Column("created_at", DATETIME),
    Column("full_text", VARCHAR(300)),
    Column("hashtags", VARCHAR(300)),
    Column("truncated", INTEGER),
    Column("display_text_range", VARCHAR(100)),
    Column("retweet_count", INTEGER),
    Column("favorite_count", INTEGER),
    Column("similarity_score", FLOAT, nullable=True),
)

tokens_table = Table(
    "tokens_count",
    metadata,
    Column("id", INTEGER, primary_key=True, autoincrement=True),
    Column("token", VARCHAR(300)),
    Column("cumulated_count", INTEGER),
    Column("popularity_count", INTEGER),
    Column("is_hashtag", BOOLEAN),
    Column("last_updated", DATETIME),
)

