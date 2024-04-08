# python lib
import os.path

# local lib
from src.common.logging_utils import get_logger
from src.common.constants import *

# 3p lib
import pandas as pd
import tweepy

log = get_logger()


def create_client():
    consumer_keys = pd.read_json(os.path.abspath('auth/twitter_consumer_keys.json'), typ='series')
    auth_tokens = pd.read_json(os.path.abspath('auth/twitter_auth_tokens.json'), typ='series')

    auth = tweepy.OAuthHandler(consumer_keys['api_key'], consumer_keys['api_key_secret'])
    auth.set_access_token(auth_tokens['access_token'], auth_tokens['access_token_secret'])

    client = tweepy.API(auth)
    client.verify_credentials()
    return client


def create_tweet(hangman, update_type: str = 'update'):
    client = create_client()
    if update_type.lower() == 'update':
        tweet = TWEET_FORMAT.format(hangman.date,
                                    hangman.round_number,
                                    hangman.hangman_ascii.get_twitter_state_ascii(),
                                    hangman.word.get_blank_word(),
                                    hangman.guessed_letters,
                                    hangman.get_form_link())
    elif update_type.upper() == 'L':
        tweet = LOSS_TWEET_FORMAT.format(hangman.word.get_word())
    elif update_type.upper() == 'W':
        tweet = WIN_TWEET_FORMAT.format(hangman.word.get_word())
    else:
        raise NotImplementedError(f'Update type {update_type} is not supported.')
    response = client.update_status(tweet)
    return response.id_str


def delete_all_tweets():
    client = create_client()
    account_name = client.verify_credentials().screen_name
    response = input('ARE YOU SURE? THIS WILL DELETE EVERY SINGLE TWEET AND CANNOT BE UNDONE?\n[y/N]: ').upper()
    if response == 'Y':
        log.info(f'Deleting all Tweets for account {account_name}...')
        for tweet in tweepy.Cursor(client.user_timeline).items():
            client.destroy_status(tweet.id)
            log.info(f'Deleted Tweet {tweet.id}')
        log.info(f'Deleted all Tweets for account {account_name}.')
