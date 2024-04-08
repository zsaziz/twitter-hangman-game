# python lib
import random
import string
import re
from sqlite3 import Row
import time
import json
from enum import Enum
from collections import Counter

# local lib
from src.hangman_utils.hangman_ascii import HangmanAscii
from src.hangman_utils.hangman_game_state import HangmanGameState, is_game_finished, InvalidStateError
from src.hangman_utils.hangman_word import HangmanWord
from src.data.words.word_utils import (
    pop_random_word,
)
from src.hangman_utils.hangman_data import HangmanData
from src.common.date_utils import get_date_from_timestamp, get_timestamp_in_seconds
from src.data.database_utils import insert_hangman, update_hangman
from src.common.constants import WIN_SYMBOL, LOSS_SYMBOL
from src.google_utils.google_forms_utils import create_form, get_responses
from src.twitter_utils.twitter_utils import create_tweet


class HangmanGame:
    def __init__(self, hangman_record: Row = None, mode: str = None):
        if hangman_record:
            construct_hangman_game_from_record(self, hangman_record)
        else:
            self.word = HangmanWord(pop_random_word(dry_run=True))
            self.created_timestamp_sec = get_timestamp_in_seconds()
            self.date = get_date_from_timestamp(self.created_timestamp_sec)
            self.hangman_id = create_hangman_id(self.word.get_word())
            self.state = HangmanGameState.Created
            self.round_number = 0
            self.hangman_ascii = HangmanAscii()
            self.guessed_letters = []
            self.result = None
            self.google_forms = {}
            self.mode = HangmanMode[mode] if mode else HangmanMode.Local.value
            insert_hangman(self)

    def next_round(self):
        form_link = ''
        if is_game_finished(self.state):
            raise InvalidStateError('Game has finished, go do something else')

        if self.state == HangmanGameState.Created:
            self.state = HangmanGameState.InProgress
            self.round_number += 1
            form_id, form_link = create_form(self)
            self.google_forms[str(self.round_number)] = [form_id, form_link]
            tweet_id = create_tweet(self)
            self.google_forms[str(self.round_number)] = [form_id, form_link, tweet_id]
        elif self.state == HangmanGameState.InProgress:
            form_id = self.get_form_id()
            responses = get_responses(form_id)
            guess_letter = get_guess_letter(responses, self.guessed_letters)
            self.guess(letter=guess_letter)

            if self.hangman_ascii.dead:
                self.state = HangmanGameState.Finished
                self.result = LOSS_SYMBOL
                self.hangman_ascii.print_state_ascii()
                tweet_id = create_tweet(self, self.result)
                self.google_forms[str(self.round_number)] = [form_id, form_link, tweet_id]
            elif self.word.word_guessed:
                self.result = WIN_SYMBOL
                self.state = HangmanGameState.Finished
                tweet_id = create_tweet(self, self.result)
                self.google_forms[str(self.round_number)] = [form_id, form_link, tweet_id]
            else:
                self.round_number += 1
                if self.google_forms.get(str(self.round_number), None):
                    raise ValueError(f'Form already exists for non-played round {self.round_number} : {self.google_forms.get(str(self.round_number), None)}')
                form_id, form_link = create_form(self)
                self.google_forms[str(self.round_number)] = [form_id, form_link]
                tweet_id = create_tweet(self)
                self.google_forms[str(self.round_number)] = [form_id, form_link, tweet_id]
        update_hangman(self)

    def get_form_id(self):
        return self.google_forms[str(self.round_number)][0]

    def get_form_link(self):
        return self.google_forms[str(self.round_number)][1]

    def guess(self, letter: str = None):
        if not letter:
            while True:
                letter = input('Guess a letter: ').upper()
                if letter.capitalize() == HangmanGameState.Abandoned.value:
                    print(f'Game has been ABANDONED, good bye.')
                    self.state = HangmanGameState.Abandoned
                    return
                if letter in self.guessed_letters:
                    print('You have already guessed this letter. Try again...')
                elif len(letter) == 0 or len(letter) > 1:
                    print('Must be a single letter. Try again...')
                elif not re.match("^[a-zA-Z]*$", letter):
                    print('Only letters A-Z allowed. Try again...')
                else:
                    break
        word = self.word.get_word()
        guess_indices = []
        for i in range(0, len(word)):
            if word[i] == letter:
                guess_indices.append(i)

        if len(guess_indices) == 0:
            self.hangman_ascii.increment_state()

        self.guessed_letters.append(letter)
        self.word.update_blank_word(self.guessed_letters)

    def print_guessed_letters(self):
        print(f'Guessed letters: {self.guessed_letters}')

    def print_round(self):
        print(f'\n== Round {self.round_number} ==')
        self.hangman_ascii.print_state_ascii()
        self.word.print_blank_word()
        self.print_guessed_letters()


def create_hangman_id(word: str):
    return f'{word}-{int(time.time())}'


def construct_hangman_game_from_record(hangman_game: HangmanGame, record: Row):
    hangman_game.hangman_id = record[HangmanData.HANGMAN_ID.value]
    hangman_game.word = HangmanWord(record[HangmanData.WORD.value])
    hangman_game.created_timestamp_sec = record[HangmanData.CREATED_TIMESTAMP_SEC.value]
    hangman_game.date = get_date_from_timestamp(hangman_game.created_timestamp_sec)
    hangman_game.state = HangmanGameState[record[HangmanData.STATE.value]]
    hangman_game.round_number = record[HangmanData.ROUND_NUMBER.value]
    hangman_game.hangman_ascii = HangmanAscii(state=record[HangmanData.HANGMAN_ASCII_STATE.value])
    guessed_letters = record[HangmanData.GUESSED_LETTERS.value]
    hangman_game.guessed_letters = guessed_letters.split(',') if len(guessed_letters) > 0 else []
    hangman_game.result = record[HangmanData.Result.value]
    hangman_game.google_forms = json.loads(record[HangmanData.GoogleForms.value])
    hangman_game.mode = record[HangmanData.Mode.value]


def get_guess_letter(responses, guessed_letters):
    if not responses or len(responses) == 0:
        return get_random_letter(guessed_letters)
    responses_counter = Counter(responses).most_common()
    letter, count = responses_counter[0]
    letters = [letter]
    for let, ct in responses_counter[1:]:
        if ct == count:
            letters.append(let)
    return random.choice(letters)


def get_random_letter(guessed_letters):
    letters = []
    for letter in list(string.ascii_uppercase):
        if letter not in guessed_letters:
            letters.append(letter)
    return random.choice(letters)


class HangmanMode(Enum):
    Online = 'Online'
    Local = 'Local'
