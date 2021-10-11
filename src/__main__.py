import time

from src.log_config import logger
from src.settings import load_config
from src.app import TwitterAnalysisApp
from tweepy import RateLimitError


def main():
    start = time.time()
    load_config()

    try:
        app = TwitterAnalysisApp()
        app.update_timeline()
        app.update_tokens_count()
        app.update_followers(app.miner.username)
        app.update_friends(app.miner.username)
        app.second_grade_search()
        return 0

    except RateLimitError:
        queries.session.commit()
        logger.exception("Requests Limit Reached")
        print(
            f"""
            ######################
            We're done for the moment!
            The process has taken: {elapsed} seconds
            You have reached the requests limit set by Twitter for a basic account.
            Please wait 15 minutes to try again.
            ######################
            """
        )
    finally:
        end = time.time()
        elapsed = round(end - start, 2)
        print(f"Elapsed time: {elapsed}")
        print()


if __name__ == "__main__":
    main()
