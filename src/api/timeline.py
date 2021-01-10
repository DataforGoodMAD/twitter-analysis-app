from typing import ContextManager, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import func, desc
from sqlalchemy.sql import select

from src.database import db_session, get_db
from src.miner import timeline_cursor
from src.models import AccountTimeline, Tweets
from src.schemas import Tweet
from src.user_env import username
from src.helpers import _build_tweet_dict, _insert_many

timeline = APIRouter(prefix="/timeline")

# CRUD Methods


@timeline.get("/", tags=["timeline"], response_model=List[Tweet])
async def get_timeline(db=Depends(get_db)):
    return db.query(AccountTimeline).all()


@timeline.get("/{tweet_id}/", tags=["timeline"], response_model=Tweet)
async def get_tweet_id(tweet_id: int, db=Depends(get_db)):
    res = db.query(AccountTimeline).filter(AccountTimeline.tweet_id == tweet_id).first() 
    if not res:
        raise HTTPException(404, detail="Tweet not found in database. Try updating from Twitter")
    return res


# Update Database From Twitter


async def newest_tweet_id(db_session: ContextManager) -> int:
    with db_session() as db:
        return db.query(func.max(Tweets.tweet_id)).scalar()


@timeline.get("/update", tags=["timeline"], response_model=List[Tweet])
async def update_timeline(db=Depends(get_db)):
    last_tweet_id: int = await newest_tweet_id(db_session)
    __import__('pdb').set_trace()
    # tl_cursor = await timeline_cursor(
    #     username=username, limit=0, since_id=last_tweet_id
    # )
    # tweets_list: List[Dict] = [await _build_tweet_dict(tweet) for tweet in tl_cursor]
    # await _insert_many(table=tweets_table, values=tweets_list)
    return {"a": "b"}
    # return await get_timeline()
