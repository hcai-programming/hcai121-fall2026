"""A terminal version of Wordle.

Guess the secret 5-letter word.  After each guess, every letter is colored:

  * green  -- the letter is in the word and in the correct spot
  * yellow -- the letter is in the word but in the wrong spot
  * gray   -- the letter is not in the word

By default you get 6 guesses; change MAX_GUESSES below or run with
`python wordle.py --guesses N`.
"""

import argparse
import random
import string

MAX_GUESSES = 6
WORD_LENGTH = 5

# Possible secret words (all common 5-letter words).
ANSWERS = [
    "about",
    "above",
    "actor",
    "acute",
    "admit",
    "adopt",
    "after",
    "again",
    "agent",
    "agree",
    "ahead",
    "alarm",
    "album",
    "alert",
    "alike",
    "alive",
    "allow",
    "alone",
    "along",
    "alter",
    "among",
    "anger",
    "angle",
    "angry",
    "apart",
    "apple",
    "apply",
    "arena",
    "argue",
    "arise",
    "aside",
    "asset",
    "audio",
    "avoid",
    "awake",
    "award",
    "aware",
    "badly",
    "baker",
    "basic",
    "beach",
    "began",
    "begin",
    "being",
    "below",
    "bench",
    "birth",
    "black",
    "blame",
    "blank",
    "blast",
    "blend",
    "bless",
    "blind",
    "block",
    "blood",
    "board",
    "boost",
    "bound",
    "brain",
    "brand",
    "brave",
    "bread",
    "break",
    "brick",
    "brief",
    "bring",
    "broad",
    "brown",
    "brush",
    "build",
    "built",
    "burst",
    "buyer",
    "cabin",
    "cable",
    "candy",
    "carry",
    "catch",
    "cause",
    "chain",
    "chair",
    "chaos",
    "charm",
    "chart",
    "chase",
    "cheap",
    "check",
    "chess",
    "chest",
    "chief",
    "child",
    "china",
    "choir",
    "chose",
    "civil",
    "claim",
    "class",
    "clean",
    "clear",
    "climb",
    "clock",
    "close",
    "cloth",
    "cloud",
    "coach",
    "coast",
    "count",
    "court",
    "cover",
    "crack",
    "craft",
    "crash",
    "crazy",
    "cream",
    "crime",
    "cross",
    "crowd",
    "crown",
    "curve",
    "cycle",
    "daily",
    "dance",
    "dealt",
    "death",
    "debut",
    "delay",
    "depth",
    "dirty",
    "doubt",
    "dozen",
    "draft",
    "drama",
    "drawn",
    "dream",
    "dress",
    "drift",
    "drink",
    "drive",
    "drove",
    "eager",
    "early",
    "earth",
    "eight",
    "elite",
    "empty",
    "enemy",
    "enjoy",
    "enter",
    "entry",
    "equal",
    "error",
    "event",
    "every",
    "exact",
    "exist",
    "extra",
    "faith",
    "false",
    "fancy",
    "fault",
    "favor",
    "fence",
    "fever",
    "fiber",
    "field",
    "fifth",
    "fifty",
    "fight",
    "final",
    "first",
    "flame",
    "flash",
    "fleet",
    "floor",
    "flour",
    "fluid",
    "focus",
    "force",
    "forth",
    "forty",
    "forum",
    "found",
    "frame",
    "fraud",
    "fresh",
    "front",
    "frost",
    "fruit",
    "fully",
    "funny",
    "ghost",
    "giant",
    "given",
    "glass",
    "globe",
    "glory",
    "grace",
    "grade",
    "grain",
    "grand",
    "grant",
    "grass",
    "grave",
    "great",
    "green",
    "greet",
    "group",
    "grown",
    "guard",
    "guess",
    "guest",
    "guide",
    "happy",
    "harsh",
    "heart",
    "heavy",
    "hello",
    "hence",
    "hobby",
    "honey",
    "honor",
    "horse",
    "hotel",
    "house",
    "human",
    "humor",
    "ideal",
    "image",
    "imply",
    "index",
    "inner",
    "input",
    "issue",
    "joint",
    "judge",
    "juice",
    "knife",
    "knock",
    "known",
    "label",
    "labor",
    "large",
    "laser",
    "later",
    "laugh",
    "layer",
    "learn",
    "least",
    "leave",
    "legal",
    "lemon",
    "level",
    "light",
    "limit",
    "local",
    "logic",
    "loose",
    "lower",
    "loyal",
    "lucky",
    "lunch",
    "magic",
    "major",
    "maker",
    "march",
    "match",
    "maybe",
    "mayor",
    "meant",
    "medal",
    "media",
    "mercy",
    "merit",
    "metal",
    "might",
    "minor",
    "minus",
    "mixed",
    "model",
    "money",
    "month",
    "moral",
    "motor",
    "mount",
    "mouse",
    "mouth",
    "movie",
    "music",
    "naval",
    "nerve",
    "never",
    "newly",
    "night",
    "noise",
    "north",
    "noted",
    "novel",
    "nurse",
    "occur",
    "ocean",
    "offer",
    "often",
    "onion",
    "order",
    "other",
    "ought",
    "outer",
    "owner",
    "paint",
    "panel",
    "paper",
    "party",
    "peace",
    "penny",
    "phase",
    "phone",
    "photo",
    "piano",
    "piece",
    "pilot",
    "pitch",
    "place",
    "plain",
    "plane",
    "plant",
    "plate",
    "point",
    "pound",
    "power",
    "press",
    "price",
    "pride",
    "prime",
    "print",
    "prior",
    "prize",
    "proof",
    "proud",
    "prove",
    "queen",
    "quick",
    "quiet",
    "quite",
    "radio",
    "raise",
    "range",
    "rapid",
    "ratio",
    "reach",
    "ready",
    "refer",
    "relax",
    "reply",
    "right",
    "rival",
    "river",
    "robot",
    "rough",
    "round",
    "route",
    "royal",
    "rural",
    "salad",
    "scale",
    "scene",
    "scope",
    "score",
    "sense",
    "serve",
    "seven",
    "shade",
    "shake",
    "shall",
    "shape",
    "share",
    "sharp",
    "sheep",
    "sheet",
    "shelf",
    "shell",
    "shift",
    "shine",
    "shirt",
    "shock",
    "shoot",
    "shore",
    "short",
    "shown",
    "sight",
    "silly",
    "since",
    "sixth",
    "sixty",
    "skill",
    "sleep",
    "slice",
    "slide",
    "small",
    "smart",
    "smile",
    "smoke",
    "snake",
    "solid",
    "solve",
    "sorry",
    "sound",
    "south",
    "space",
    "spare",
    "speak",
    "speed",
    "spend",
    "spent",
    "spice",
    "split",
    "spoke",
    "sport",
    "staff",
    "stage",
    "stair",
    "stake",
    "stand",
    "start",
    "state",
    "steam",
    "steel",
    "steep",
    "stick",
    "still",
    "stock",
    "stone",
    "stood",
    "store",
    "storm",
    "story",
    "strip",
    "study",
    "stuff",
    "style",
    "sugar",
    "suite",
    "sunny",
    "super",
    "sweet",
    "table",
    "taken",
    "taste",
    "teach",
    "thank",
    "theme",
    "there",
    "these",
    "thick",
    "thing",
    "think",
    "third",
    "those",
    "three",
    "throw",
    "tiger",
    "tight",
    "title",
    "toast",
    "today",
    "token",
    "topic",
    "total",
    "touch",
    "tough",
    "tower",
    "trace",
    "track",
    "trade",
    "trail",
    "train",
    "treat",
    "trend",
    "trial",
    "tribe",
    "trick",
    "truck",
    "truly",
    "trust",
    "truth",
    "twice",
    "under",
    "union",
    "unite",
    "unity",
    "until",
    "upper",
    "upset",
    "urban",
    "usage",
    "usual",
    "valid",
    "value",
    "video",
    "virus",
    "visit",
    "vital",
    "vocal",
    "voice",
    "waste",
    "watch",
    "water",
    "wheat",
    "wheel",
    "where",
    "which",
    "while",
    "white",
    "whole",
    "whose",
    "woman",
    "world",
    "worry",
    "worse",
    "worst",
    "worth",
    "would",
    "wound",
    "write",
    "wrong",
    "wrote",
    "yield",
    "young",
    "youth",
]

# ANSI escape codes for coloring a single letter tile.
GREEN = "\033[1;97;42m"  # white text on green
YELLOW = "\033[1;97;43m"  # white text on yellow
GRAY = "\033[1;97;100m"  # white text on gray
RESET = "\033[0m"


def load_dictionary():
    """Return the set of words accepted as guesses.

    Uses the system dictionary when available so players can guess any real
    5-letter word, and always includes the answer list as a fallback.
    """
    valid = set(ANSWERS)
    try:
        with open("/usr/share/dict/words") as f:
            for line in f:
                word = line.strip().lower()
                if len(word) == WORD_LENGTH and word.isalpha():
                    valid.add(word)
    except OSError:
        pass  # no system dictionary; only words from ANSWERS are accepted
    return valid


def score_guess(guess, answer):
    """Return a list of colors ('green', 'yellow', 'gray') for each letter.

    Repeated letters are handled the way Wordle does: a letter is only
    marked yellow if there are unmatched copies of it left in the answer.
    E.g. guessing "geese" against "green" gives green, yellow, green,
    gray, gray -- the final 'e' is gray because both e's in the answer
    have already been accounted for.
    """
    colors = ["gray"] * WORD_LENGTH

    # First pass: mark greens and count the answer letters not yet matched.
    remaining = {}
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            colors[i] = "green"
        else:
            remaining[a] = remaining.get(a, 0) + 1

    # Second pass: mark yellows, consuming remaining letters left to right.
    for i, g in enumerate(guess):
        if colors[i] != "green" and remaining.get(g, 0) > 0:
            colors[i] = "yellow"
            remaining[g] -= 1

    return colors


def colorize(guess, colors):
    """Return the guess as a string of colored letter tiles."""
    codes = {"green": GREEN, "yellow": YELLOW, "gray": GRAY}
    return "".join(
        f"{codes[c]} {letter.upper()} {RESET}" for letter, c in zip(guess, colors)
    )


def keyboard_status(letter_info):
    """Return the alphabet colored by what is known about each letter."""
    codes = {"green": GREEN, "yellow": YELLOW, "gray": GRAY}
    tiles = []
    for letter in string.ascii_lowercase:
        color = letter_info.get(letter)
        if color:
            tiles.append(f"{codes[color]}{letter.upper()}{RESET}")
        else:
            tiles.append(letter.upper())
    return " ".join(tiles)


def play(max_guesses=MAX_GUESSES):
    answer = random.choice(ANSWERS)
    valid_words = load_dictionary()

    # Best known status for each guessed letter (green beats yellow beats gray).
    rank = {"gray": 0, "yellow": 1, "green": 2}
    letter_info = {}

    print(
        f"\nWelcome to Wordle! Guess the {WORD_LENGTH}-letter word."
        f" You have {max_guesses} guesses.\n"
    )

    guesses_used = 0
    while guesses_used < max_guesses:
        prompt = f"Guess {guesses_used + 1}/{max_guesses}: "
        guess = input(prompt).strip().lower()

        if len(guess) != WORD_LENGTH or not guess.isalpha():
            print(f"  Please enter a {WORD_LENGTH}-letter word.\n")
            continue
        if guess not in valid_words:
            print("  Not in word list.\n")
            continue

        guesses_used += 1
        colors = score_guess(guess, answer)
        for letter, color in zip(guess, colors):
            if rank[color] > rank.get(letter_info.get(letter), -1):
                letter_info[letter] = color

        print(f"  {colorize(guess, colors)}")
        print(f"  {keyboard_status(letter_info)}\n")

        if guess == answer:
            print(
                f"Congratulations! You got it in {guesses_used} "
                f"{'guess' if guesses_used == 1 else 'guesses'}."
            )
            return

    print(f"Out of guesses! The word was: {answer.upper()}")


def main():
    parser = argparse.ArgumentParser(description="Play Wordle in the terminal.")
    parser.add_argument(
        "--guesses",
        type=int,
        default=MAX_GUESSES,
        help=f"number of allowed guesses (default {MAX_GUESSES})",
    )
    args = parser.parse_args()
    if args.guesses < 1:
        parser.error("--guesses must be at least 1")
    play(max_guesses=args.guesses)


if __name__ == "__main__":
    main()
