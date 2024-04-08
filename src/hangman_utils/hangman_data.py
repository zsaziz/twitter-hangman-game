# python lib
from enum import Enum


class HangmanData(Enum):
    HANGMAN_ID = 'HangmanId'
    WORD = 'Word'
    CREATED_TIMESTAMP_SEC = 'CreatedTimestampSec'
    STATE = 'State'
    ROUND_NUMBER = 'RoundNumber'
    HANGMAN_ASCII_STATE = 'HangmanAsciiState'
    GUESSED_LETTERS = 'GuessedLetters'
    Result = 'Result'
    GoogleForms = 'GoogleForms'
    Mode = 'Mode'
