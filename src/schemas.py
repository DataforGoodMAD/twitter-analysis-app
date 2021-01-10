from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: int
    screen_name: str
    location: str
    protected: bool
    followers_count: int
    friends_count: int
    created_at: datetime
    # favourites_count: int
    statuses_count: int
    default_profile_image = bool
    is_friend: Optional[bool]
    is_follower: Optional[bool]
    last_status: Optional[datetime] = None
    reviewed: bool
    similarity_score: Optional[float] = None

    class Config:
       orm_mode=True 


class Tweet(BaseModel):
    tweet_id: int
    user_id: int
    created_at: datetime
    full_text: str
    hashtags: str
    truncated: int
    display_text_range: str
    retweet_count: int
    favorite_count: int
    similarity_score: Optional[int] = None

    class Config:
       orm_mode=True 


class Token(BaseModel):
    id: int
    token: str
    cumulated_count: int
    popularity: int
    is_hashtag: bool
    last_updated: datetime
    
    class Config:
       orm_mode=True 
    
