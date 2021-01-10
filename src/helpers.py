from typing import Any, List, Dict

async def _build_tweet_dict(status) -> Dict:
    tweet = {
        "tweet_id": status.id,
        "user_id": status.author.id,
        "created_at": status.created_at,
        "full_text": status.full_text,
        "hashtags": str(
            list(
                map(
                    lambda hashtag: hashtag["text"],
                    status._json.get("entities", None).get("hashtags", None),
                )
            )
        ),
        "truncated": status.truncated,
        "display_text_range": str(status.display_text_range),
        "retweet_count": status.retweet_count,
        "favorite_count": status.favorite_count,
        "similarity_score": (
            status.similarity if hasattr(status, "similarity") else None
        ),
    }
    return tweet


async def _build_user_dict(user, force_is_follower: bool = False, force_is_friend: bool = False):
    user = {
        "id": user.id,
        "screen_name": user.screen_name,
        "location": user.location,
        "protected": user.protected,
        "followers_count": user.followers_count,
        "friends_count": user.friends_count,
        "created_at": user.created_at,
        # "favourites_count": user.favourites_count,
        "statuses_count": user.statuses_count,
        # "default_profile_image": user.default_profile_image,
        "is_follower": 1 if force_is_follower else None,
        "is_friend": 1 if force_is_friend else None,
        "last_status": (user.status.created_at if hasattr(user, "status") else None),
        "reviewed": 0,
        "similarity_score": (user.similarity if hasattr(user, "similarity") else None),
    }
    return user


async def _update_ff_in_db(field: str, values: List[Dict]):
    query = users_table.update().values({f"{field}": 0})
    await db.execute(query)
    query = f"""
            INSERT INTO users 
            VALUES(:id, :screen_name, :location, :protected, :followers_count, 
            :friends_count, :created_at, :statuses_count, :is_follower, 
            :is_friend, :last_status, :reviewed, :similarity_score)
            ON CONFLICT(id)
            DO UPDATE SET {field}=1;
            """
    return await db.execute_many(query, values)


async def _fetch_many(table, values: List[Dict]):
    query = table.select()
    return await db.execute_many(query)


async def _insert_many(table, values: List[Dict]):
    query = table.insert()
    return await db.execute_many(query, values)
