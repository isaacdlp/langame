# LanGame

Gamified multi-lingual cards. Learn as easy as 1-2-3! :)

## Step 1: Create your own word map

Modify the Excel file `langame.xlsx` to contain the languages and words that you want to train.
These are the formatting rules:

* One concept per row, one language per column
    * The first row contains the language names. As a convention we use the short language codes but it can be whatever.
    * The first column contains your "native" tongue, the one you are most confortable with. It acts as the index.
* Each cell contains the translation for that concept and language
    * Leave empty if that concept does not apply / exist
    * The translation can contain multiple words, separated by `, ` (e.g. `Bye, Goodbye`)
    * Optionally, assign **gender**
        * In some languages gender plays a very important role in language formation
        * From the Excel palette, color the cell:
            * BLUE for MASCULINE
            * PINK for FEMENINE
            * GREEN for NEUTRAL
        * Don't color it if gender does not apply / exist

## Step 2: Update the game's dictionary

In order to speed up execution the game uses a pre-compiled `langame.json` dictionary file in JSON format.
Run the following line to update that file:

`python langame.py update`

## Step 3: Play!

Run the following line to play the game:

`python langame.py play`

* In each round you will have a word to guess in a given language.
    * Full matches score one point, partial matches score half.
    * A full match only considers letters (i.e. ignores whitespace and symbols)
    * A partial match additionally ignores:
        * Stress marks (e.g. accepts Spanish "o" for "ó" or "ô")
        * Some inflection marks (e.g. Russian "ь" or "ъ")
        * Some particular letter groups (e.g. Russian "и" for "ы" or "й")
        * Customize this as needed for your learning
    * Run as many rounds as you want, stop at any point by typing `@`
    * You will visualize some basic performance stats
    * Repeat as often as you want!

### Parameters

There are a couple of command-line parameters that can be used to customize the experience:

`python langame.py play <lang_focus> <word_focus>`

`lang_focus` can be a language or comma-separated language list to focus on.
Only questions from these languages will be asked if found.
`ALL` refers to all possible languages (no focus)

* `python langame.py play ru`
* `python langame.py play it,pt`

`word_focus` is the number of concepts to focus on, starting from the end.
LanGame keeps the concepts stored in an ordered dictionary, so that you can focus on the most recently added concepts.

* `python langame.py play it,pt 100`
* `python langame.py play all 25`