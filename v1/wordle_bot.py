from utils import get_clue, words, valid_word_given_clues, load_first_word_values, to_index

version = 1


def word_value(word, valid_words):
    """
    This function determines the average number of valid words available for the second guess if this word is used
    for the first guess. It works like this: If a word as the answer, generates some clue, then it is also a valid
    word for the next guess. The set of words generating a given clue as the ANSWER is equivalent to the set of words
    that are valid GUESSES for the next guess. So, we determine how many words generate each clue.
    Consider clue 0. If there are x words in clue 0, then we know, if one of those words is the answer, any of those x
    words could be next. i.e. there are x next valid words. Since there are x words that generate this clue, and each
    of those has x valid second guesses, then this clue contributes x*x to the mean. Finally, we divide the sum by the
    length of words to produce a mean. Note: the mean is over the list of words, even though the sum is over a list of
    clues. In reality we are summing over the list of words, its just that we have sorted the words into each clue,
    making is seem like the sum is over the list of clues. This is why we divide by len(words), and not 243
    """
    num_words_generating_clue = [0] * 243
    for answer in valid_words:
        num_words_generating_clue[get_clue(word, answer)] += 1

    return sum([x*x for x in num_words_generating_clue]) / len(valid_words)


first_word_values = load_first_word_values(version, lambda w: word_value(w, words))


def next_words(guesses, clues):
    if len(guesses) == 0:
        return first_word_values

    valid_words = [w for w in words if valid_word_given_clues(guesses, clues, w)]
    word_values = [(w, word_value(w, valid_words)) for w in valid_words]
    return sorted(word_values, key=lambda x: x[1])


if __name__ == '__main__':
    print(next_words(['train'], [to_index([0, 0, 0, 0, 2])]))
