import os
from dotenv import load_dotenv

from tw_miner import TwitterMiner
from tw_processor import TwitterProcessor

load_dotenv()


if __name__ == "__main__":
    username = os.getenv('username')
    processor = TwitterProcessor()
    miner = TwitterMiner(username)
    cursor = miner.timelineCursorRequest(user_id=miner.username, limit=5)

    for tweet in cursor:
        miner.postTweetToDB([tweet])
        processor.updateCounter([tweet])
