# python lib
from enum import Enum

class HangmanGameState(Enum):
    Created = 'Created'
    InProgress = 'InProgress'
    Finished = 'Finished'
    Abandoned = 'Abandoned'


def is_game_finished(state):
    return state == HangmanGameState.Finished


class InvalidStateError(Exception):
    pass
