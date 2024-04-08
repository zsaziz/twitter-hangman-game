# python lib
import random
from datetime import datetime
import os
import requests

# local lib
from src.common.logging_utils import get_logger

log = get_logger()

WORD_DICTIONARY_URL = 'https://gist.githubusercontent.com/alpha-tango/c3d2645817cf4af2aa45/raw/6c2b253372462aa9764240b15e48a785dd693148/Hangman_wordbank'

BASE_DIR = os.path.join('data', 'words')
LAST_UPDATED_FILE_NAME = os.path.join(BASE_DIR, 'word_list_last_updated.txt')
WORD_LIST_FILE_NAME = os.path.join(BASE_DIR, 'word_list.txt')
ORIGINAL_WORD_LIST_FILE_NAME = os.path.join(BASE_DIR, 'original_word_list.txt')


def get_latest_word_dictionary():
    page = requests.get(WORD_DICTIONARY_URL)
    word_list = page.text.split(', ')

    log.info(f'Successfully retrieved latest list of {len(word_list)}. Saving to file...')

    save_to_file('\n'.join(word_list), ORIGINAL_WORD_LIST_FILE_NAME)
    save_to_file('\n'.join(word_list), WORD_LIST_FILE_NAME)
    save_to_file(str(datetime.today()), LAST_UPDATED_FILE_NAME)

    log.info(f'Successfully saved word list to file {ORIGINAL_WORD_LIST_FILE_NAME}')


def save_to_file(content, file_path):
    with open(file_path, 'w') as file:
        file.write(content)


# Selects random word and removes it from file
def pop_random_word(dry_run=False):
    with open(WORD_LIST_FILE_NAME, 'r') as file:
        word_list = [word for word in file.readlines()]
    with open(WORD_LIST_FILE_NAME, 'w') as file:
        word = random.choice(word_list)
        if not dry_run:
            word_list.remove(word)
        file.write(''.join(word_list))
    return word.strip().upper()


def get_blank_word(word: str):
    return ('_ ' * (len(word)))[:-1]
