import tweepy
from dotenv import dotenv_values, load_dotenv
import os
from .log_config import logger


def config_check():
    load_dotenv()
    keys = ["CONSUMER_KEY", "CONSUMER_SECRET_KEY", "USER_SCREEN_NAME"]
    if all([dotenv_values().get(key, None) for key in keys]):
        # print("Welcome back! Let's go!")
        return True
    return False
    # else:
    #     return firstTimeConfig()


def verify_config(consumer_key, consumer_secret_key, user_screen_name):
    try:
        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret_key)
        api = tweepy.API(auth)
        user = api.get_user(user_screen_name)
        return {"user": user.name, "description": user.description}
        # print(
        #     f'This is the description I have found on your account:\n"{user.description}"'
        # )
        # confirmation = input("Is it the right one? [y/n]:")
        # if confirmation != "y":
        #     print(
        #         "Seems like something went wrong. Please enter again your Twitter Username:"
        #     )
        #     user_screen_name = input("Please enter your Twitter Username:")
        #     continue

        # print(
        #     "Great! Your setup is complete. Let's start working! Please, do not close your terminal until the process is finished. You'll now when it's done."
        # )
    except Exception as e:
        logger.exception(f"Exception occurred: {e}")
        return e


def save_config(consumer_key, consumer_secret_key, user_screen_name):
    with open(".env", "w+") as config_file:
        c_key = f"CONSUMER_KEY={consumer_key}\n"
        c_s_key = f"CONSUMER_SECRET_KEY={consumer_secret_key}\n"
        user = f"USER_SCREEN_NAME={user_screen_name}"
        env_file_input = c_key + c_s_key + user
        config_file.write(env_file_input)
        load_dotenv()
