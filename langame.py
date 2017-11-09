from openpyxl import load_workbook
from random import choice
import warnings, sys
warnings.simplefilter("ignore")


genders = {
    4: "M",
    6: "N",
    9: "F"
}

filebase = "langame"
action = "play"
if len(sys.argv) > 1:
    action = sys.argv[1]

if action == "update":

    wb = load_workbook(filename="%s.xlsx" % filebase)

    sh = wb["WORDLDS"]

    langs = []

    col = 1
    while True:
        col += 1
        lang = sh.cell(row=1, column=col).value
        if lang is None:
            break
        else:
            langs.append(lang)

    words = {}
    concept = None

    row = 1
    while True:
        row += 1
        if concept is not None:
            words[concept] = word
        concept = sh.cell(row=row, column=1).value
        if concept is None:
            break
        word = {}
        for col, lang in enumerate(langs):
            con = {}
            col += 2
            cell = sh.cell(row=row, column=col)
            sym = cell.value
            if sym is not None:
                con["sym"] = sym
                gender = cell.fill.start_color.index
                gen = genders[gender] if gender in genders else None
                if gen is not None:
                    con["gen"] = gen
                word[lang] = con

# In Python 3 keys() is an iterator, not a list
points = 0
for num in range(1, 11):
    concepts = list(words.keys())
    concept = choice(concepts)
    lang = choice(langs)
    word = words[concept]
    if lang in word:
        con = word[lang]
        sym = con["sym"]
        gen = con["gen"] if "gen" in con else None

    print("Question %i: '%s' in %s" % (num, concept, lang))
    response = input()
    if response.lower() == sym.lower():
        print("Correct!")
        points += 0.5
    else:
        print("Wrong! It is %s" % sym)
    if gen is not None:
        print("Which gender is it? [M]asculine, [N]eutral or [F]emenine?")
        response = input()
        if response.lower() == gen.lower():
            print("Correct!")
            points += 0.5
        else:
            print("Wrong! It is %s" % gen)
    else:
        points += 0.5

print("Total points: %d" % points)
print("Thank you for playing!")