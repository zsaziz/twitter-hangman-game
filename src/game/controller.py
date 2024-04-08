# local lib
from src.hangman_utils.hangman_game import HangmanGame
from src.hangman_utils.hangman_data import HangmanData
from src.data.database_utils import get_today_in_progress_games, get_today_finished_games, cleanup_in_progress_hangman_games, delete_all_rows
from src.common.logging_utils import get_logger
from src.twitter_utils.twitter_utils import delete_all_tweets

log = get_logger()


def main(delete_all: bool = False):
    if delete_all:
        delete_all_rows()
        delete_all_tweets()

    finished_games = get_today_finished_games()
    if finished_games:
        hangman_record = finished_games[0]
        log.info(f'Hangman game {hangman_record[HangmanData.HANGMAN_ID.value]} is in '
                 f'{hangman_record[HangmanData.STATE.value]} state.')
        return

    in_progress_games = get_today_in_progress_games()
    if not in_progress_games:
        hangman_game = HangmanGame(mode='Online')
    else:
        hangman_game = HangmanGame(hangman_record=in_progress_games[0], mode='Online')
        cleanup_in_progress_hangman_games(in_progress_games[1:])

    hangman_game.next_round()
