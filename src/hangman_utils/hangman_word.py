# local lib
from src.data.words.word_utils import get_blank_word


class HangmanWord:
    def __init__(self, word):
        self.word = word
        self.blank_word = get_blank_word(self.word)
        self.word_guessed = False

    def print_blank_word(self):
        print(f'\n{self.blank_word}\n')

    def get_blank_word(self):
        return f'\n{self.blank_word}\n'

    def update_blank_word_with_guess(self, guess_letter, guess_indices):
        blank_word = [letter for letter in self.blank_word]
        for index in guess_indices:
            blank_word[index * 2] = guess_letter.upper()
        self.blank_word = ''.join(blank_word)
        if '_' not in self.blank_word:
            self.word_guessed = True

    def update_blank_word(self, guessed_letters):
        if len(guessed_letters) == 0:
            return
        for letter in guessed_letters:
            guess_indices = []
            for i in range(0, len(self.word)):
                if self.word[i] == letter:
                    guess_indices.append(i)
            self.update_blank_word_with_guess(letter, guess_indices)

    def get_word(self):
        return self.word
