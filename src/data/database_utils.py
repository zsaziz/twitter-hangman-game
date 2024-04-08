# local lib
from src.data.database_constants import TABLE_NAME, DATABASE_NAME
from src.hangman_utils.hangman_game_state import HangmanGameState
from src.hangman_utils.hangman_data import HangmanData
from src.common.date_utils import get_todays_date
from src.common.logging_utils import get_logger

# python lib
import sqlite3
from datetime import timedelta
import json
import re
from typing import List

log = get_logger(__name__)


def create_table(table_name: str, columns: List[tuple]):
    """
    Function to create table.
    :param table_name: name of table
    :param columns: list of tuples with name (0) and type (1) (e.g. [('colName', 'TEXT')]
    :return: None
    """
    cursor, connection = start_connection()
    command = f'CREATE TABLE {table_name} ({generate_columns_command(columns)})'
    cursor.execute(command)

    close_connection(cursor, connection)


def insert_hangman(hangman, table_name: str = TABLE_NAME):
    cursor, connection = start_connection()

    command = f'INSERT INTO {table_name} VALUES ('
    command += f"'{hangman.hangman_id}', '{hangman.word.get_word()}', {hangman.created_timestamp_sec}, "
    command += f"'{hangman.state.value}', {hangman.round_number}, {hangman.hangman_ascii.state}, "
    command += f"'{convert_guessed_letters_csv(hangman.guessed_letters)}', '{hangman.result}', "
    command += f"'{convert_google_forms_json(hangman.google_forms)}', '{hangman.mode.value}')"

    cursor.execute(command)
    connection.commit()

    close_connection(cursor, connection)


def update_hangman(hangman, table_name: str = TABLE_NAME):
    cursor, connection = start_connection()

    columns_to_update = [
        (HangmanData.STATE.value, f"'{hangman.state.value}'"),
        (HangmanData.ROUND_NUMBER.value, hangman.round_number),
        (HangmanData.HANGMAN_ASCII_STATE.value, hangman.hangman_ascii.state),
        (HangmanData.GUESSED_LETTERS.value, f"'{convert_guessed_letters_csv(hangman.guessed_letters)}'"),
        (HangmanData.Result.value, f"'{hangman.result}'"),
        (HangmanData.GoogleForms.value, f"'{convert_google_forms_json(hangman.google_forms)}'")
    ]
    command = f'UPDATE {table_name}\n'
    command += f'SET {generate_columns_command(columns_to_update, delimiter="=")}\n'
    command += f'WHERE {HangmanData.HANGMAN_ID.value} = "{hangman.hangman_id}"'

    cursor.execute(command)
    connection.commit()

    close_connection(cursor, connection)


def get_today_in_progress_games():
    cursor, connection = start_connection()

    today, tomorrow = get_today_and_tomorrow_dates()

    log.info(f'Getting {HangmanGameState.InProgress.value} Hangman for date {today.date()}...')

    command = f'SELECT * FROM {TABLE_NAME}\n'
    command += f'WHERE {HangmanData.CREATED_TIMESTAMP_SEC.value} >= {int(today.timestamp())} AND ' \
               f'{HangmanData.CREATED_TIMESTAMP_SEC.value} < {int(tomorrow.timestamp())}\n'
    command += f'AND {HangmanData.STATE.value} = "{HangmanGameState.InProgress.value}"\n'
    command += f'ORDER BY {HangmanData.CREATED_TIMESTAMP_SEC.value} DESC'
    response = cursor.execute(command).fetchall()

    log.info(f'Retrieved {len(response)} {HangmanGameState.InProgress.value} Hangman records for date {today.date()}')

    close_connection(cursor, connection)
    return response


def get_today_finished_games():
    cursor, connection = start_connection()

    today, tomorrow = get_today_and_tomorrow_dates()

    log.info(f'Getting {HangmanGameState.Finished.value} Hangman for date {today.date()}...')

    command = f'SELECT * FROM {TABLE_NAME}\n'
    command += f'WHERE {HangmanData.CREATED_TIMESTAMP_SEC.value} >= {int(today.timestamp())} AND ' \
               f'{HangmanData.CREATED_TIMESTAMP_SEC.value} < {int(tomorrow.timestamp())}\n'
    command += f'AND {HangmanData.STATE.value} = "{HangmanGameState.Finished.value}"\n'
    command += f'ORDER BY {HangmanData.CREATED_TIMESTAMP_SEC.value} DESC'
    response = cursor.execute(command).fetchall()

    log.info(f'Retrieved {len(response)} {HangmanGameState.Finished.value} Hangman records for date {today.date()}')

    close_connection(cursor, connection)
    return response


def cleanup_in_progress_hangman_games(records: List[sqlite3.Row]):
    cursor, connection = start_connection()

    today, tomorrow = get_today_and_tomorrow_dates()

    if not records:
        log.info(f'No records to cleanup for date {today}')
        return

    log.info(f'Cleaning up {len(records)} records for date {today}...')
    for row in records:
        hangman_id = row[HangmanData.HANGMAN_ID.value]

        command = f'UPDATE {TABLE_NAME}\n'
        command += f'SET {HangmanData.STATE.value}="{HangmanGameState.Abandoned.value}"\n'
        command += f'WHERE {HangmanData.HANGMAN_ID.value} = "{hangman_id}"'

        cursor.execute(command)
        log.info(f'Updating {HangmanData.STATE.value} to {HangmanGameState.Abandoned.value} for {HangmanData.HANGMAN_ID.value} : {hangman_id}')
    connection.commit()
    log.info(f'Cleaned up {len(records)} records for date {today}')

    close_connection(cursor, connection)


def generate_columns_command(columns: List[tuple], delimiter: str = ' '):
    """
    :param columns: list of tuples with name (0) and type (1) (e.g. [('colName', 'TEXT')]
    :param delimiter delimiter to separate column name and value [e.g. '=']
    :return: SQL format list of columns returned as a string [e.g "name TEXT, number INTEGER"]
    """
    columns_command = ''
    for col in columns:
        columns_command += f'{col[0]}{delimiter}{col[1]}, '
    # [:-2] is for removing trailing ", "
    return columns_command[:-2]


def get_google_forms(hangman_id: str):
    cursor, _ = start_connection()
    command = f'SELECT {HangmanData.GoogleForms.value} FROM {TABLE_NAME} ' \
              f'WHERE {HangmanData.HANGMAN_ID.value} = "{hangman_id}"'
    google_forms = cursor.execute(command).fetchone()[HangmanData.GoogleForms.value]
    print(google_forms)
    return json.loads(google_forms)


def convert_guessed_letters_csv(guessed_letters: List[str]):
    return ','.join(guessed_letters)


def convert_google_forms_json(google_forms: dict):
    return json.dumps(google_forms)


def camelCase_to_snake_case(string: str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()


def delete_all_rows():
    cursor, connection = start_connection()

    response = input('ARE YOU SURE? THIS WILL WIPE THE DATABASE AND CANNOT BE UNDONE?\n[y/N]: ').upper()
    if response == 'Y':
        command = f'DELETE FROM {TABLE_NAME}'
        cursor.execute(command)
        connection.commit()
        log.info(f'All rows have been deleted from {TABLE_NAME}')
    close_connection(cursor, connection)


def get_today_and_tomorrow_dates():
    today = get_todays_date(return_datetime=True)
    tomorrow = today + timedelta(days=1)
    return today, tomorrow


def close_connection(cursor, connection):
    cursor.close()
    connection.close()


def start_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return cursor, connection


def add_column(col_name: str, col_type: str):
    cursor, connection = start_connection()
    command = f'ALTER TABLE {TABLE_NAME} ADD COLUMN "{col_name}" {col_type}'
    log.info(f'Adding column with command: {command}')
    cursor.execute(command)
    connection.commit()
    log.info(f'Added column with command {command}')
