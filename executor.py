#!/usr/bin/env python3

import argparse
import json
import sys

import matplotlib.pyplot as plt
import matplotlib
from utils import to_index, from_index, get_clue, answers, words
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from time import sleep
from os.path import exists
from datetime import date
from typing import Any
import importlib

matplotlib.use('agg')
driver = None


def get_bot_response(bot, answer, guesses=None):
    guesses = guesses or []
    clues = [get_clue(g, answer) for g in guesses]
    while len(guesses) == 0 or clues[-1] != 242:
        guesses.append(bot.next_words(guesses, clues)[0][0])
        clues.append(get_clue(guesses[-1], answer))

    if hasattr(bot, 'mark_solved'):
        bot.mark_solved()
    return guesses, clues


def evaluate(bot):
    print('\n' * 8)
    bins = [0] * 6
    worst_words = []
    worst_score = 0
    results = {'mean': 0, 'worst': 0, 'distribution': {}, 'results': []}
    for i, answer in enumerate(answers):
        move_up = len(bins) + 3
        response = get_bot_response(bot, answer)[0]
        score = len(response)
        results['results'].append({'answer': answer, 'score': score, 'response': response})
        if score > worst_score:
            worst_score = score
            worst_words = [answer]
        elif score == worst_score:
            worst_words.append(answer)
        if score > len(bins):
            bins += [0] * (score - len(bins))
        bins[score - 1] += 1
        print(f'\033[{move_up}FAnswers tested: {i + 1}/{len(answers)}' + ' ' * 10)
        worst_words_line = f"Worst words: {', '.join(worst_words[:5])}" + ('...' if len(worst_words) > 5 else '')
        print(worst_words_line + ' ' * (60 - len(worst_words_line)))
        mean = sum([(j + 1) * b for j, b in enumerate(bins)]) / sum(bins)
        print(f'Mean: {mean:.3f}' + ' ' * 10)
        for j, b in enumerate(bins):
            ratio = b / sum(bins)
            fractional = round(8 * ((20 * ratio) % 1))
            bar = '\u2588' * int(20 * ratio) + (chr(0x2588 + 8 - fractional) if fractional > 0 else '')
            print(f'{j + 1: 2d} {bar} {100 * ratio:.2f}%' + ' ' * 20)

    mean = sum([(j + 1) * b for j, b in enumerate(bins)]) / sum(bins)
    results['mean'] = mean
    results['worst'] = len(bins)
    results['distribution'] = {i + 1: b for i, b in enumerate(bins)}
    with open(f'v{bot.version}/results.json', 'w') as f:
        json.dump(results, f, indent=2)

    if hasattr(bot, 'mark_complete'):
        bot.mark_complete(mean)

    fig, ax = plt.subplots()
    rects = ax.bar(range(1, len(bins) + 1), [100 * b / sum(bins) for b in bins])
    ax.set_xlabel('Number of guesses')
    ax.set_ylabel('Frequency (%)')
    ax.set_title(f'Distribution of Wordle bot (v{bot.version}) performance ($\\mu$ = {mean:.3f})')
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')
    plt.savefig(f'v{bot.version}/distribution.png')


def display_bot_response(bot, answer, guesses):
    responses = get_bot_response(bot, answer, guesses)
    for word, clue in zip(*responses):
        clue = from_index(clue)
        for i in range(5):
            print(['\033[30;47m', '\033[30;103m', '\033[30;102m'][clue[i]], word[i], sep='', end='')
        print('\033[0m')


class ElementIsRevealed(object):
    """An expectation for checking is the element has been revealed

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, element):
        self.element = element

    def __call__(self, arg):
        if self.element.get_attribute('data-state') != 'tbd':
            return self.element
        else:
            return False


def play_in_browser(bot, starting_words, answer=None):
    global driver
    day = date.today().toordinal()
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://www.nytimes.com/games/wordle/index.html')
    wait = WebDriverWait(driver, 10)
    browser_state = None
    if exists('browser_state.json'):
        with open('browser_state.json') as f:
            browser_state = json.load(f)
            if browser_state['last_played'] == day:
                if browser_state['yesterday'] is not None:
                    driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);",
                                          'nyt-wordle-statistics', browser_state['yesterday'])
            else:
                driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);",
                                      'nyt-wordle-statistics', browser_state['today'])

    if answer is not None:
        driver.execute_script(f"document.querySelector('game-app').solution = arguments[0];", answer)

    # game_app = driver.find_element(By.CSS_SELECTOR, 'game-app').shadow_root
    # game_modal = game_app.find_element(By.CSS_SELECTOR, 'game-modal').shadow_root
    driver.find_element(By.CSS_SELECTOR, '[class^="Modal-module_closeIcon"]').click()
    guesses, clues = starting_words, []
    sleep(0.5)
    while len(clues) < 6:
        root = driver.find_element(By.CSS_SELECTOR, ':root')

        if len(guesses) == len(clues):
            word = bot.next_words(guesses, clues)[0][0]
            guesses.append(word)
        else:
            word = guesses[len(clues)]

        for letter in word:
            root.send_keys(letter)
            sleep(0.2)
        root.send_keys(Keys.RETURN)
        wait.until(ElementIsRevealed(
            driver.find_element(
                By.CSS_SELECTOR,
                f'[class^="Board-module_board_"] > div:nth-child({len(clues) + 1}) > div:last-child > div')))

        clue = [0] * 5
        for i in range(len(word)):
            evaluation = driver.find_element(
                By.CSS_SELECTOR,
                f'[class^="Board-module_board_"] > div:nth-child({len(clues) + 1}) > div:nth-child({i+1}) > div')\
                .get_attribute('data-state')
            if evaluation == 'present':
                clue[i] = 1
            elif evaluation == 'correct':
                clue[i] = 2
        clue = to_index(clue)
        clues.append(clue)
        if clue == 242:
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '[class^="Modal-module_closeIcon"]')))
            close_icon = driver.find_element(By.CSS_SELECTOR, '[class^="Modal-module_closeIcon"]')
            wait.until(ec.element_to_be_clickable(close_icon))
            close_icon.click()
            if browser_state is None or browser_state['last_played'] != day:
                statistics = driver.execute_script("return window.localStorage.getItem(arguments[0]);",
                                                   'nyt-wordle-statistics')
                with open('browser_state.json', 'w') as f:
                    json.dump({'last_played': day,
                               'yesterday': browser_state['today'] if browser_state is not None else None,
                               'today': statistics}, f, indent=2)

            return
        sleep(2)


def main():
    def word(w):
        w = w.lower()
        if w not in words:
            raise ValueError(f'{w} is not in the word list')
        return w

    parser = argparse.ArgumentParser(description="A bot capable of playing Wordle. "
                                                 "To play today's Wordle, type wordle-bot")
    parser.add_argument('-v', '--version', default=3, type=int,
                        help='The version of the Wordle bot to use')
    parser.add_argument('-e', '--eval', '--evaluate', action='store_true',
                        help='The evaluate flag runs the bot in evaluation mode. In this mode, the bot plays all '
                             'possible answer words, and the performance of the bot is displayed')
    parser.add_argument('-t', '--terminal', action='store_true',
                        help='The bot\'s response will be displayed in the terminal instead of on the Wordle website. '
                             'This is useful if you do not have the ChromeDriver installed, and is also much quicker '
                             'than playing in the browser. If this argument is used, an answer must be provided using '
                             'the \'-a\' argument')
    parser.add_argument('-a', '--answer', type=word,
                        help='If supplied, the bot will play with the given word as the answer. If not supplied, the '
                             'bot will play today\'s Wordle')
    parser.add_argument('starting words', nargs='*', type=word,
                        help='The words the bot will start with. After the bot has guessed these words, the bot will '
                             'attempt to find the answer within the fewest guesses given the clues it has received. If '
                             'no starting words are given, the bot has full control over all of its guesses')

    args = parser.parse_args()
    try:
        module: Any = importlib.import_module(f'v{args.version}.wordle_bot')
        bot = module.Bot(args.version)
    except ModuleNotFoundError:
        sys.stderr.write(f'Version {args.version} does not exist\n')
        return

    if args.eval:
        evaluate(bot)
    elif args.terminal:
        display_bot_response(bot, args.answer, vars(args)['starting words'])
    else:
        play_in_browser(bot, vars(args)['starting words'], args.answer)


if __name__ == '__main__':
    main()
