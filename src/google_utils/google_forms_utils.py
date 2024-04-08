# local lib
from src.google_utils.google_apis import create_service
from src.common.constants import *
from src.common.logging_utils import get_logger

# python lib
import os.path
import json
import csv
import string

log = get_logger()

CREDENTIALS = os.path.abspath('auth/google_credentials.json')
API_NAME = 'forms'
API_VERSION = 'v1'
# To update scopes, delete token file and rerun
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.body.readonly"
]


def get_forms_client():
    return create_service(CREDENTIALS, API_NAME, API_VERSION, SCOPES).forms()


def update_form(hangman, form_id):
    forms_client = get_forms_client()
    form_description = f'{hangman.hangman_ascii.get_state_ascii()}\n{hangman.word.get_blank_word()}'
    update_body = {
        'requests': [
            {
                'updateFormInfo': {
                    'info': {
                        'description': form_description
                    },
                    'updateMask': 'description'
                }
            },
            {
                'createItem': {
                    'item': {
                        'title': 'Guess a letter',
                        'description': f'These letters have already been guessed {hangman.guessed_letters}',
                        'questionItem': {
                            'question': {
                                'required': True,
                                'choiceQuestion': {
                                    'type': 'RADIO',
                                    'options': generate_choices_for_update(hangman.guessed_letters),
                                    'shuffle': False
                                }
                            }
                        }
                    },
                    'location': {
                        'index': 0
                    }
                }
            }
        ]
    }

    result = forms_client.batchUpdate(formId=form_id, body=update_body).execute()
    log.info(f'Response after updating form {result}')


def get_responses(form_id):
    forms_client = get_forms_client()
    result = forms_client.responses().list(formId=form_id).execute()
    responses = []
    try:
        for response in result['responses']:
            answer = list(response['answers'].values())[0]['textAnswers']['answers']
            responses.extend([val['value'] for val in answer])
    except KeyError:
        return responses

    return responses


def generate_choices_for_update(guessed_letters=None):
    if guessed_letters is None:
        guessed_letters = []
    body = []
    for letter in list(string.ascii_uppercase):
        if letter not in guessed_letters:
            body.append({
                'value': letter
            })
    return body


def create_form(hangman):
    hangman_id = hangman.hangman_id
    hangman_date = hangman.date

    log.info(f'Creating new google form for hangman id {hangman_id}...')
    forms_client = get_forms_client()

    form_name = FORM_NAME_FORMAT.format(hangman_date, hangman.round_number)
    form = {
        "info": {
            "title": form_name,
            "document_title": form_name
        }
    }
    result = forms_client.create(body=form).execute()
    form_id = result[FORM_ID]
    form_link = result[FORM_LINK]

    log.info(f'Created google form for hangman id {hangman_id} with form id {form_id}')

    log.info(f'Updating form {form_id}...')
    update_form(hangman, form_id)
    log.info(f'Updated form {form_id}')
    return form_id, form_link
