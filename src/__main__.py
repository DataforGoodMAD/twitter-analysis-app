import time

from src.app import TwitterAnalysisApp
from src.log_config import logger
from src.settings import load_config
from tweepy import RateLimitError


def main():
    start = time.time()
    load_config()
    app = TwitterAnalysisApp()

    try:
        app.create_tables()
        app.update_timeline()
        app.update_tokens_count()
        app.update_followers(app.miner.username)
        app.update_friends(app.miner.username)
        app.second_grade_search()

    except RateLimitError:
        app.db.session.commit()
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

    except Exception as e:
        print(e)

    finally:
        app.export_tables_to_csv()
        end = time.time()
        elapsed = round(end - start, 2)
        print(f"Elapsed time: {elapsed}")
        print()
        return 0
