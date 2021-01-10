from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.sql.operators import exists

from src.database import get_db
from src.miner import (
    followers_cursor,
    friends_cursor,
    get_users_from_twitter,
    twitter_followers_list,
)
from src.models import Users
from src.schemas import Token, Tweet, User
from src.user_env import username
from src.helpers import _build_user_dict, _insert_many, _update_ff_in_db

users = APIRouter(prefix="/users")

# CRUD Methods


@users.get("/", tags=["users"], response_model=List[User])
async def get_users(followers: Optional[bool] = False, friends: Optional[bool] = False):
    query = users_table.select()
    return await database.fetch_all(query)


@users.get("/{user_id}/", tags=["users"], response_model=User)
async def get_user_id(user_id: int):
    __import__('pdb').set_trace()
    query = users_table.select().where(users_table.c.id == user_id)
    res = await database.fetch_one(query)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return res


# Update Database From Twitter

# FIXME: These methods are slow. A method to not check all followers every time is needed.


@users.get("/update_followers", tags=["users"], response_model=List[User])
async def update_followers():
    # Get New Followers From Twitter
    users_cursor = await followers_cursor(screen_name=username, limit=0)
    followers = []
    for user in users_cursor:
        followers.append(await _build_user_dict(user, force_is_follower=True))
    await _update_ff_in_db("is_follower", followers)
    return await get_users()


@users.get("/update_friends", tags=["users"], response_model=List[User])
async def update_friends():
    # Get New Followers From Twitter
    users_cursor = await friends_cursor(screen_name=username, limit=0)
    friends = []
    for user in users_cursor:
        friends.append(await _build_user_dict(user, force_is_friend=True))
    await _update_ff_in_db("is_friend", friends)
    return await get_users()


@users.get("/main_user", tags=["timeline"])
async def get_user_id():
    res = await get_users_from_twitter([username])
    user = await _build_user_dict(res[0])
    query = users_table.select().where(users_table.c.id == user["id"]) 
    value = await database.fetch_one(query)
    if not value:
        query = users_table.insert()
        await database.execute(query, user)
    return user


