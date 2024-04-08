from datetime import date


HANGMAN_ASCII_STATES = [
'''
  +---+
      |
      |
      |
      |
      |
=========''',
'''
  +---+
  |   |
      |
      |
      |
      |
=========''',
'''
  +---+
  |   |
  O   |
      |
      |
      |
=========''',
'''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========''',
'''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''',
'''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========''',
'''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========''',
'''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========''']


class HangmanAscii:
    def __init__(self, created_date: date = None, state: int = None):
        self.state = state if state else 0
        self.create_date = created_date if created_date else date.today()
        self.dead = False

    def increment_state(self):
        self.state += 1
        if self.state == len(HANGMAN_ASCII_STATES) - 1:
            self.dead = True

    def print_state_ascii(self):
        print(HANGMAN_ASCII_STATES[self.state])

    def get_state_ascii(self):
        return HANGMAN_ASCII_STATES[self.state]

    def get_twitter_state_ascii(self):
        return TWITTER_HANGMAN_ASCII_STATES[self.state]


TWITTER_HANGMAN_ASCII_STATES = [
'''
+-----+
            |
            |
            |
            |
            |
=========''',
'''
 +-----+
  |         |
            |
            |
            |
            |
=========''',
'''
 +-----+
  |         |
 O        |
            |
            |
            |
=========''',
'''
 +-----+
  |         |
 O        |
  |         |
            |
            |
=========''',
'''
 +-----+
  |         |
 O        |
/|         |
            |
            |
=========''',
'''
 +-----+
  |         |
 O        |
/|\        |
            |
            |
=========''',
'''
 +-----+
  |         |
 O        |
/|\        |
/           |
             |
=========''',
'''
 +-----+
  |         |
 O        |
/|\        |
/ \        |
             |
========='''
]