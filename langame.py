from openpyxl import load_workbook
from random import choice
import warnings, sys, json
warnings.simplefilter("ignore")


genders = {
    4: "M",
    6: "N",
    9: "F"
}

filebase = "langame"
focus = None

action = "update"
if len(sys.argv) > 1:
    action = sys.argv[1]
    if len(sys.argv) > 2:
        focus = sys.argv[2].upper().split(",")

if action == "update":

    # Update the JSON dictionary

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
            if len(word) > 0:
                words[concept] = word
        concept = sh.cell(row=row, column=1).value
        if concept is None:
            break
        word = {}
        for col, lang in enumerate(langs):
            con = []
            col += 2
            cell = sh.cell(row=row, column=col)
            sym = cell.value
            if sym is not None:
                con.append(sym)
                gender = cell.fill.start_color.index
                gen = genders[gender] if gender in genders else None
                if gen is not None:
                    con.append(gen)
                word[lang] = con

    print("Writing %i words to JSON" % len(words))
    with open("%s.json" % filebase, "w") as f:
        json.dump(words, f)

else:

    # Play the game!

    with open("%s.json" % filebase, "r") as f:
        words = json.load(f)

    concepts = list(words.keys())
    used = []

    # In Python 3 keys() is an iterator, not a list
    points = 0
    for num in range(1, 11):
        concept = None
        lang = None
        sym = None
        gen = None
        for i in range(100):
            concept = choice(concepts)
            word = words[concept]
            langs = list(word.keys())
            lang = choice(langs).upper()
            if focus is None or lang in focus:
                pair = "%s@%s" % (concept, lang)
                if pair not in used:
                    used.append(pair)
                    con = word[lang]
                    sym = con[0]
                    gen = con[1] if len(con) > 1 else None
                    break

        if sym is None:
            print("Not enough words!")
            break

        print("Question %i: '%s' in %s" % (num, concept, lang))
        response = input()
        if response.lower() == sym.lower():
            print("RIGHT! It is '%s'" % sym)
            points += 0.5
        else:
            print("WRONG! It is '%s'" % sym)
        if gen is not None:
            print("Which gender is it? [M]asculine, [N]eutral or [F]emenine?")
            response = input()
            if response.lower() == gen.lower():
                print("RIGHT! It is '%s'" % gen)
                points += 0.5
            else:
                print("WRONG! It is '%s'" % gen)
        else:
            points += 0.5

    print("Total points: %d" % points)
    print("Thank you for playing!")