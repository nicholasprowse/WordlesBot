# WordlesBot
A bot that plays Wordle close to optimally. The bot can either play in the browser on the official Wordle website, 
or in the terminal in a simulation of the game

## Setup

Chromedriver is required for the bot to play Wordle in the browser. Make sure Google Chrome is installed, and then install ChromeDriver.
CromeDriver is avalable as [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads). 
Make sure to check your Google Chrome version, and install the relevant version of ChromeDriver. The ChromeDriver executable must be placed in a 
directory in your PATH. Use `echo $PATH` to see which directories are in your PATH

## Usage

`./wordle-bot [-h] [-v VERSION] [-e] [-t] [-a ANSWER] [starting words ...]`

Simply use `./wordle-bot` with no arguments to play todays Wordle in the browser.

`-v VERSION, --version VERSION` can be specified as 1, 2 or 3 to specify which version of the bot to use. 
Version 3 is the default option, and performs better than the other versions.

`-e, --eval, --evaluate` is a flag that indicates that the performance of the bot should be evaluated. 
In this mode, the bot plays all possible answer words, and the performance of the bot is displayed in the terminal.
Additionally, a bar plot displaying the distribution of the bots scores is saved to the directory containing the relevant bot version,
and a json file containing the bots response for every answer word is saved

`-t, --terminal` is a flag that indicates that the bot should play in the terminal, rather than the browser.
This is useful if you do not have the ChromeDriver installed, and is also much quicker than playing in the browser. 
If this argument is used, an answer must be provided using the `-a, --answer` argument

`-a ANSWER, --answer ANSWER` specifies the answer to the Wordle. This works both in the browser and the terminal. 
This is required in the terminal, but if playing in the browser it is optional and if not supplied, todays answer is used

`starting words` allows you to specify one or more starting words that the bot must use. 
This allows you to compare what the bot does in a certain situation compared to you
