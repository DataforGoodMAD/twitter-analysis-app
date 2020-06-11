import tweepy
from dotenv import dotenv_values, load_dotenv
import os
from log_config import logger


def configCheck():
    load_dotenv()
    keys = ["CONSUMER_KEY", "CONSUMER_SECRET_KEY", "USER_SCREEN_NAME"]
    if all([dotenv_values().get(key, None) for key in keys]):
        print("Welcome back! Let's go!")
        return True
    else:
        return firstTimeConfig()


def firstTimeConfig():
    while True:
        consumer_key = input('Please enter your Twitter "CONSUMER_KEY":')
        consumer_secret_key = input('Please enter your Twitter "CONSUMER_SECRET_KEY":')
        user_screen_name = input("Please enter your Twitter Username:")
        try:
            while True:
                auth = tweepy.AppAuthHandler(consumer_key, consumer_secret_key)
                api = tweepy.API(auth)
                user = api.get_user(user_screen_name)
                print(
                    f'This is the description I have found on your account:\n"{user.description}"'
                )
                confirmation = input("Is it the right one? [y/n]:")
                if confirmation != "y":
                    print(
                        "Seems like something went wrong. Please enter again your Twitter Username:"
                    )
                    user_screen_name = input("Please enter your Twitter Username:")
                    continue
                else:
                    break
            with open(".env", "a") as f:
                env_file_input = f"CONSUMER_KEY={consumer_key}\nCONSUMER_SECRET_KEY={consumer_secret_key}\nUSER_SCREEN_NAME={user_screen_name}"
                f.write(env_file_input)
            print(
                "Great! Your setup is complete. Let's start working! Please, do not close your terminal until the process is finished. You'll now when it's done."
            )
            load_dotenv()
            break
        except Exception:
            logger.exception("Exception occurred")
            print("Something went wrong. Please enter your data again.")
            continue


if __name__ == "__main__":
    configCheck()
