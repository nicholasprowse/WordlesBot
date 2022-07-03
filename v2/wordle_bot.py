from utils import get_clue, words, valid_word_given_clues, load_first_word_values

version = 2


def word_value(word, valid_words):
    num_words_generating_clue = [0] * 243
    for answer in valid_words:
        num_words_generating_clue[get_clue(word, answer)] += 1

    return sum([x*x for x in num_words_generating_clue[:-1]]) / len(valid_words)


first_word_values = load_first_word_values(version, lambda w: word_value(w, words))


def next_words(guesses, clues):
    if len(guesses) == 0:
        return first_word_values

    valid_words = [w for w in words if valid_word_given_clues(guesses, clues, w)]
    word_values = [(w, word_value(w, valid_words)) for w in words if w not in guesses]
    return sorted(word_values, key=lambda x: x[1])
