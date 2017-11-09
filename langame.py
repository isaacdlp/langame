from openpyxl import load_workbook
from random import choice
import warnings, sys, json, re, unicodedata
warnings.simplefilter("ignore")


filebase = "langame"
focus = None

action = "play"
if len(sys.argv) > 1:
    action = sys.argv[1]
    if len(sys.argv) > 2:
        focus = sys.argv[2].upper().split(",")


genders = {
    4: "M",
    5: "F",
    6: "N"
}

inputs = {
    "M": "M, М",
    "F": "F, Ф",
    "N": "N, Н"
}

clean_reg = re.compile("[^\w ]+")
spaces_reg = re.compile("[ ]+")
normal_reg = re.compile("[À-ÿьъ]+")

def do_clean(text):
    text = clean_reg.sub("", text).lower()
    text = spaces_reg.sub(" ", text)
    return text

def do_normal(text):
    for raw in normal_reg.findall(text):
        normal = unicodedata.normalize("NFD", raw).encode("ascii", "ignore").decode("utf-8")
        text = text.replace(raw, normal)
    text = spaces_reg.sub(" ", text)
    return text

def do_eval(guess, solutions):
    match = "WRONG"
    points = 0
    clean_guess = do_clean(guess)
    normal_guess = do_normal(clean_guess)
    for solution in solutions.split(", "):
        clean_sol = do_clean(solution)
        if clean_guess == clean_sol:
            match = "RIGHT"
            points = 0.5
            break
        else:
            normal_sol = do_normal(clean_sol)
            if normal_guess == normal_sol:
                match = "ALMOST"
                points = 0.25
    return match, points


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
    rounds = 0
    score = 0.0
    while True:
        rounds += 1
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

        print("Round %i [%.2f] '%s' in %s" % (rounds, score, concept, lang))
        guess = input()
        if guess == "@":
            break
        result, points = do_eval(guess, sym)
        print("%s! It is '%s'" % (result, sym))
        if gen is not None:
            print("Which gender is it? [M]asculine, [N]eutral or [F]emenine?")
            guess = input()
            result, pts = do_eval(guess, inputs[gen])
            print("%s! It is '%s'" % (result, gen))
            points += pts
        else:
            points *= 2
        score += points

    rounds -= 1
    accuracy = score / rounds if rounds > 1 else 0
    print("Total points [%.2f] rounds [%i] accuracy [%.2f%s]" % (score, rounds, accuracy, "%"))
    print("Thank you for playing!")