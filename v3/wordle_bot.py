from utils import get_clue, words, valid_word_given_clues, word_frequencies, load_first_word_values
from math import log2, exp


def frequency_transform(f):
    return 1 / (1 + exp(-6 * (f - 2e-6) / 1e-6))


word_frequencies = {w: frequency_transform(f) for w, f in word_frequencies.items()}


class Bot:
    def __init__(self, version):
        self.version = version
        self.second_word_lookup = {}
        initial_entropy = sum([p * log2(1 / p) for p in word_frequencies.values()])
        self.first_word_values = \
            load_first_word_values(version, lambda w: Bot.word_value(w, 0, initial_entropy, word_frequencies))

    @staticmethod
    def word_value(word, num_guesses, entropy, valid_word_frequencies):
        prob_clue = [0] * 243
        for answer in valid_word_frequencies:
            prob_clue[get_clue(word, answer)] += valid_word_frequencies[answer]

        entropy_after = entropy - sum([p*log2(1/p) for p in prob_clue if p > 0])
        if word in valid_word_frequencies:
            return valid_word_frequencies[word] * (num_guesses + 1) + \
                   (1 - valid_word_frequencies[word]) * (entropy_after + num_guesses + 1.01)
        return num_guesses + 1.01 + entropy_after

    def next_words(self, guesses, clues):
        if len(guesses) == 0:
            return self.first_word_values

        if len(guesses) == 1:
            if guesses[0] in self.second_word_lookup:
                if self.second_word_lookup[guesses[0]][clues[0]] is not None:
                    return self.second_word_lookup[guesses[0]][clues[0]]
            else:
                self.second_word_lookup[guesses[0]] = [None] * 243

        valid_word_frequencies = {w: f for w, f in word_frequencies.items()
                                  if valid_word_given_clues(guesses, clues, w)}
        total = sum(valid_word_frequencies.values())
        valid_word_frequencies = {w: f / total for w, f in valid_word_frequencies.items()}
        entropy = sum([p*log2(1/p) for p in valid_word_frequencies.values()])

        word_values = [(w, Bot.word_value(w, len(guesses), entropy, valid_word_frequencies))
                       for w in words if w not in guesses]
        word_values = sorted(word_values, key=lambda x: x[1])
        if len(guesses) == 1:
            self.second_word_lookup[guesses[0]][clues[0]] = word_values
        return word_values


def valid_words(guesses, answer):
    clues = [get_clue(guess, answer) for guess in guesses]
    valid_word_frequencies = {w: f for w, f in word_frequencies.items() if valid_word_given_clues(guesses, clues, w)}
    total = sum(valid_word_frequencies.values())
    valid_word_frequencies = {w: f / total for w, f in valid_word_frequencies.items()}
    print(valid_word_frequencies)
