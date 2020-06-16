import tweepy

from src.db_models import Base
from src.db_queries import DBQueries
from src.features import (
    secondGradeSearch,
    updateFollowers,
    updateFriends,
    updateTimeline,
    updateTokensCount,
)
from src.log_config import logger
from src.settings import configCheck, firstTimeConfig
from src.tw_miner import TwitterMiner
from src.tw_processor import TwitterProcessor


def main():

    configCheck()

    try:
        logger.info(Base.metadata.create_all())
        print("Database Loaded.")

        processor = TwitterProcessor()
        print("TwitterProcessor instance created")
        queries = DBQueries()
        print("DBQueries instance created")
        miner = TwitterMiner()
        print("TwitterMiner instance created")

        updateTimeline(processor, queries, miner)
        updateTokensCount(processor, queries)
        updateFollowers(queries, miner, miner.username)
        updateFriends(queries, miner, miner.username)
        secondGradeSearch(miner, processor, queries)

    except tweepy.RateLimitError:
        queries.session.commit()
        logger.exception("Exception occurred")
        print(
            "We're done for the moment! We have reached the requests limit set by Twitter for a basic account. Please wait 15 minutes to try again."
        )
        return 0


if __name__ == "__main__":
    pass
