import logging
import os
import sys
import warnings

import tweepy

from db_models import Base
from db_queries import DBQueries
from tw_miner import TwitterMiner
from tw_processor import TwitterProcessor
from settings import configCheck, firstTimeConfig
from features import (
    updateTimeline,
    updateTokensCount,
    updateFollowers,
    updateFriends,
    secondGradeSearch,
)


def main():

    logger = logging.getLogger("log")

    configCheck()
    # Disable warnings for production. Change PYTHONWARNINGS to 'default' to debug.
    python_warnings = os.getenv("PYTHONWARNINGS")
    warnings.simplefilter(python_warnings)

    try:
        Base.metadata.create_all()
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
        print(
            "We're done for the moment! We have reached the requests limit set by Twitter for a basic account. Please wait 15 minutes to try again."
        )
        return 0


if __name__ == "__main__":
    main()
