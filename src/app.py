from log_config import logger
import os
import sys
import warnings
import contextlib

import tweepy

from db_models import Base
from db_queries import DBQueries
from features import (
    secondGradeSearch,
    updateFollowers,
    updateFriends,
    updateTimeline,
    updateTokensCount,
)
from settings import configCheck, firstTimeConfig
from tw_miner import TwitterMiner
from tw_processor import TwitterProcessor


def main():

    configCheck()
    # Disable warnings for production. Change PYTHONWARNINGS to 'default' to debug.
    python_warnings = os.getenv("PYTHONWARNINGS")
    warnings.simplefilter(python_warnings)

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
        logging.exception("Exception occurred")
        print(
            "We're done for the moment! We have reached the requests limit set by Twitter for a basic account. Please wait 15 minutes to try again."
        )
        return 0


if __name__ == "__main__":
    main()
