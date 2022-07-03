import json
import os
from os.path import exists

os.chdir('/Users/nicholasprowse/Documents/Programming/PycharmProjects/wordles_optimiser')
with open('words.json') as ff:
    word_frequencies = json.load(ff)

with open('answers.json') as ff:
    answers = json.load(ff)

words = sorted(list(word_frequencies.keys()))
word_index_lookup = {w: i for i, w in enumerate(words)}


"""
If there is a double letter, there are a number of possibilities
Grey Grey - Letter is not in the word
Grey Yellow - Only one of the yellow letter is in the word
Yellow Yellow - Two (or more) of the yellow letter
Grey Green - Letter only appears once, and the green one is correct
Yellow Green - Letter appears more than once and the green one is correct
Green Green - Both are correct, but there may be more
"""
clue_lookup = None


def get_clue(guess, answer):
    global clue_lookup
    if clue_lookup is None:
        if exists('clues.bin'):
            with open('clues.bin', 'rb') as f:
                clue_lookup = f.read()
        else:
            clue_lookup = bytearray(len(words) ** 2)
            for i in range(len(words)):
                for j in range(len(words)):
                    clue_lookup[i * len(words) + j] = compute_clue(words[i], words[j])
            clue_lookup = bytes(clue_lookup)
            with open('clues.bin', 'wb') as f:
                f.write(clue_lookup)

    return clue_lookup[word_index_lookup[guess] * len(words) + word_index_lookup[answer]]


def compute_clue(guess, answer):
    """0: not in word (grey), 1: in wrong spot (yellow), 2: correct (green)"""
    answer = list(answer)
    clue = [0] * 5
    for i, c in enumerate(guess):
        if c == answer[i]:
            clue[i] = 2
            answer[i] = '0'

    for i, c in enumerate(guess):
        if c in answer and clue[i] == 0:
            clue[i] = 1
            answer[answer.index(c)] = '0'
    return to_index(clue)


def valid_word_given_clues(clue_words, clues, guess):
    for clue, clue_word in zip(clues, clue_words):
        if get_clue(clue_word, guess) != clue:
            return False

    return True


def to_index(clue):
    index = 0
    for i in range(5):
        index *= 3
        index += clue[i]
    return index


def from_index(index):
    clue = [0] * 5
    for i in range(4, -1, -1):
        clue[i] = index % 3
        index //= 3

    return clue


def load_first_word_values(version, word_value):
    if not exists(f'v{version}/word_values.json'):
        first_word_values = [(w, word_value(w)) for w in words]
        with open(f'v{version}/word_values.json', 'w') as f:
            json.dump(first_word_values, f, indent=2)

    with open(f'v{version}/word_values.json') as f:
        return sorted(json.load(f), key=lambda x: x[1])


def test_get_clue():
    test_cases = [('smoke', 'faint', [0, 0, 0, 0, 0]),
                  ('taint', 'faint', [0, 2, 2, 2, 2]),
                  ('canes', 'faint', [0, 2, 1, 0, 0]),
                  ('shook', 'joint', [0, 0, 1, 0, 0]),
                  ('shook', 'looks', [1, 0, 2, 1, 1]),
                  ('leech', 'hoard', [0, 0, 0, 0, 1]),
                  ('igloo', 'tooth', [0, 0, 0, 1, 1]),
                  ('tooth', 'roost', [1, 2, 2, 0, 0]),
                  ('eater', 'water', [0, 2, 2, 2, 2]),
                  ('tater', 'water', [0, 2, 2, 2, 2])]

    for guess, answer, clue in test_cases:
        test_clue = get_clue(guess, answer)
        if clue != test_clue:
            print(f'Incorrect clue for guess of {guess} with answer {answer}. Expected {clue}, but got {test_clue}')


if __name__ == '__main__':
    test_get_clue()
