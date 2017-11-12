# Copyright (c) 2017 Isaac de la Pena (isaacdlp@alum.mit.edu)
#
# Open-sourced according to the MIT LICENSE
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from openpyxl import load_workbook
from random import choice
import collections as co
import warnings, sys, json, re, unicodedata
warnings.simplefilter("ignore")


filebase = "langame"
lang_focus = None
word_focus = 0

action = "play"
if len(sys.argv) > 1:
    action = sys.argv[1]
    if len(sys.argv) > 2:
        lang_focus = sys.argv[2].upper().split(",")
        map(lambda x: x.upper(), lang_focus)
        if "ALL" in lang_focus:
            lang_focus = None
        if len(sys.argv) > 3:
            try:
                word_focus = int(sys.argv[3])
            except:
                print("Wrong word focus number")


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

note_reg = re.compile("\([^\)]+\)")
clean_reg = re.compile("[^\w]+")
normal_reg = re.compile("[À-ÿьъ]+")
repeat_reg = re.compile("((\w)\\2{1,})")
replacements = (("й", "и"), ("ы", "и"), ("щ", "ш"), ("в", "б"))

def do_clean(text):
    for raw in note_reg.findall(text):
        text = text.replace(raw, "")
    text = clean_reg.sub("", text).lower()
    return text

def do_normal(text):
    for raw in normal_reg.findall(text):
        normal = unicodedata.normalize("NFD", raw).encode("ascii", "ignore").decode("utf-8")
        text = text.replace(raw, normal)
    for replacement in replacements:
        text = text.replace(replacement[0], replacement[1])
    for repeat in repeat_reg.findall(text):
        text = text.replace(repeat[0], repeat[1])
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
    sh = wb[wb.sheetnames[0]]
    langs = []

    col = 1
    while True:
        col += 1
        lang = sh.cell(row=1, column=col).value
        if lang is None:
            break
        else:
            langs.append(lang.upper())

    words = co.OrderedDict()
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
        json.dump(list(words.items()), f)

else:

    # Play the game!

    with open("%s.json" % filebase, "r") as f:
        words = co.OrderedDict(json.load(f))

    # In Python 3 keys() is an iterator, not a list
    concepts = list(words.keys())
    if word_focus > 0 and not word_focus > len(concepts):
        concepts = concepts[-word_focus:]
    used = []


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
            if lang_focus is None or lang in lang_focus:
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
    accuracy = (score / rounds) * 100 if rounds > 0 else 0
    print("Total points [%.2f] rounds [%i] accuracy [%.2f%%]" % (score, rounds, accuracy))
    print("Thank you for playing!")