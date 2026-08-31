#!/usr/bin/env python3
"""Wordle in the terminal.

The computer picks a secret five-letter word; you have a limited number of
guesses (six by default) to find it.  After each guess, every letter is
scored:

    green   -- right letter in the right spot
    yellow  -- right letter in the wrong spot
    gray    -- letter does not appear in the word

Repeated letters behave the way the real game handles them: each letter of
the answer can color at most one tile, and green tiles are claimed first.

Examples:
    python wordle.py                   play with the defaults
    python wordle.py --guesses 8       allow eight guesses
    python wordle.py --words my.txt    draw answers from your own word list
    python wordle.py --answer stern    fix the answer (useful for testing)
    python wordle.py --no-color        plain text instead of colored tiles
"""

import argparse
import os
import random
import string
import sys
from collections import Counter

WORD_LENGTH = 5
DEFAULT_GUESSES = 6          # change this, or use --guesses on the command line

# Tile states.
GREEN, YELLOW, GRAY, UNUSED = "green", "yellow", "gray", "unused"

# How informative each state is.  Used to upgrade the on-screen keyboard:
# once a letter has shown yellow it never falls back to gray, and so on.
RANK = {UNUSED: 0, GRAY: 1, YELLOW: 2, GREEN: 3}

ANSI = {
    GREEN: "\033[1;97;42m",     # bold white on green
    YELLOW: "\033[1;30;43m",    # bold black on yellow
    GRAY: "\033[1;97;100m",     # bold white on gray
}
RESET = "\033[0m"
DIM = "\033[2m"

MARK = {GREEN: "G", YELLOW: "Y", GRAY: "."}      # used by --no-color
EMOJI = {GREEN: "🟩", YELLOW: "🟨", GRAY: "⬜"}   # end-of-game summary grid

PRAISE = ("Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!")

# The answer pool: common five-letter words.  Edit freely -- anything listed
# here can come up as the secret word -- or point --words at your own file.
ANSWERS = """
about above actor acute admit adopt adult after again agent
agree ahead alarm album alert alien alike alive allow alone
along alter among anger angle angry apart apple apply arena
argue arise armor aroma array arrow aside asset audio audit
avoid awake award aware badge badly baker basic basis beach
beard beast began begin being belly below bench berry birth
black blade blame blank blast blaze bleed blend bless blind
block blood bloom board boast bonus boost booth bound brain
brand brave bread break breed brick bride brief bring broad
brown brush build bunch burst buyer cabin cable camel candy
cargo carry catch cause chain chair chalk charm chart chase
cheap check cheek cheer chess chest chief child chill choir
chose civil claim clash class clean clear clerk click cliff
climb clock close cloth cloud coach coast color comet comic
coral couch could count court cover crack craft crane crash
crazy cream crime crisp cross crowd crown crumb crush curve
cycle daily dairy dance dealt death debut delay delta dense
depth devil diary dirty ditch dodge doing donor doubt dozen
draft drain drama drank dream dress dried drift drill drink
drive drove dying eager eagle early earth eight elbow elder
elect elite empty enemy enjoy enter entry equal error essay
event every exact exist extra fable faint fairy faith false
fancy fatal fault favor feast fence fever fiber field fifth
fifty fight final first flame flash fleet flesh float flock
flood floor flour fluid flush focus force forge forth forty
forum found frame fraud fresh front frost fruit fully funny
ghost giant given glass globe glory glove going grace grade
grain grand grant grape graph grasp grass grave great green
greet grief grill gross group grove growl grown guard guess
guest guide habit happy harsh haste hatch haven heart heavy
hedge hello hence hobby honey honor horse hotel house human
humor hurry ideal image imply index inner input irony issue
ivory jeans jelly jewel joint jolly judge juice knife knock
known label labor large laser later laugh layer learn lease
least leave legal lemon level light limit linen liver local
logic loose loyal lucky lunar lunch lyric magic major maker
mango maple march match maybe mayor meant medal media mercy
merge merit merry metal meter midst might minor minus mixed
model moist money month moral motor mount mouse mouth movie
music naive nasty naval nerve never newly night noble noise
north novel nurse occur ocean offer often olive onion opera
orbit order organ other ought ounce outer owner oxide ozone
paint panel panic paper party pasta patch pause peace peach
pearl pedal penny phase phone photo piano piece pilot pinch
pitch pizza place plain plane plant plate plaza pluck point
polar porch pound power press price pride prime print prior
prize proof proud prove pulse pupil purse queen query quest
queue quick quiet quilt quite quote radar radio raise rally
ranch range rapid ratio reach react ready realm rebel refer
reign relax relay reply rider ridge rifle right rigid risky
rival river roast robin robot rocky roman rough round route
royal rugby ruler rural sadly saint salad salon sandy sauce
scale scare scene scent scope score scout scrap screw seize
sense serve seven shade shaft shake shall shame shape share
sharp sheep sheet shelf shell shift shine shiny shirt shock
shoot shore short shout shown sight silly since sixty skill
skirt slate sleep slice slide slope small smart smell smile
smoke snack snake solar solid solve sorry sound south space
spare spark speak speed spell spend spice spike spine split
spoke sport spray squad stack staff stage stain stair stake
stamp stand stare start state steam steel steep steer stick
stiff still stock stone stood store storm story stove strap
straw strip study stuff style sugar suite sunny super surge
swear sweat sweep sweet swift swing sword table taken taste
teach tempo tenth thank theft theme there these thick thief
thing think third those three threw throw thumb tiger tight
timer title toast today token tooth topic torch total touch
tough tower toxic trace track trade trail train trait treat
trend trial tribe trick troop truck truly trunk trust truth
tumor tutor twice twist uncle under union unite unity until
upper upset urban usage usual vague valid value vapor vault
venue verse video vigor villa vinyl viola virus visit vital
vivid vocal voice voter wagon waist waste watch water weary
weigh weird whale wheat wheel where which while white whole
whose widow width windy witch woman world worry worse worst
worth would wound woven wrist write wrong wrote yacht yeast
yield young youth
""".split()


# --------------------------------------------------------------------------
# Game logic
# --------------------------------------------------------------------------

def score_guess(guess: str, answer: str) -> list:
    """Return a color (GREEN / YELLOW / GRAY) for each letter of ``guess``.

    Green tiles are claimed first.  The answer's remaining letters are then
    handed out as yellows from left to right, each one at most once, so
    repeated letters behave exactly as in Wordle (guessing EEEEE against
    CRANE lights up a single green tile and nothing else).
    """
    # Letters of the answer not already matched green, with multiplicity.
    unmatched = Counter(a for g, a in zip(guess, answer) if g != a)

    scores = []
    for g, a in zip(guess, answer):
        if g == a:
            scores.append(GREEN)
        elif unmatched[g] > 0:
            scores.append(YELLOW)
            unmatched[g] -= 1
        else:
            scores.append(GRAY)
    return scores


def update_tracker(tracker: dict, guess: str, scores: list) -> None:
    """Record the best-known state of each guessed letter."""
    for g, s in zip(guess, scores):
        if RANK[s] > RANK[tracker[g]]:
            tracker[g] = s


# --------------------------------------------------------------------------
# Display
# --------------------------------------------------------------------------

def tile(letter: str, state: str) -> str:
    """One colored tile, e.g. a white-on-green ' A '."""
    if state == UNUSED:
        return f" {letter.upper()} "
    return f"{ANSI[state]} {letter.upper()} {RESET}"


def show_board(history: list, max_guesses: int, color: bool) -> None:
    print()
    for guess, scores in history:
        if color:
            print("   " + " ".join(tile(g, s) for g, s in zip(guess, scores)))
        else:
            print("   " + "  ".join(guess.upper()))
            print("   " + "  ".join(MARK[s] for s in scores))
    if color:
        empty = " ".join(f"{DIM} · {RESET}" for _ in range(WORD_LENGTH))
        for _ in range(max_guesses - len(history)):
            print("   " + empty)


def show_letters(tracker: dict, color: bool) -> None:
    """Show what is known about each letter (a small on-screen keyboard)."""
    if color:
        print()
        for pad, row in zip((0, 2, 6), ("qwertyuiop", "asdfghjkl", "zxcvbnm")):
            print(" " * (3 + pad) + " ".join(tile(c, tracker[c]) for c in row))
    else:
        groups = {GREEN: [], YELLOW: [], GRAY: []}
        for c in string.ascii_lowercase:
            if tracker[c] in groups:
                groups[tracker[c]].append(c.upper())
        parts = []
        if groups[GREEN]:
            parts.append("placed: " + " ".join(groups[GREEN]))
        if groups[YELLOW]:
            parts.append("in word: " + " ".join(groups[YELLOW]))
        if groups[GRAY]:
            parts.append("absent: " + " ".join(groups[GRAY]))
        if parts:
            print("   [" + "   |   ".join(parts) + "]")


def share_grid(history: list, max_guesses: int, won_in) -> str:
    """The classic emoji summary you can paste anywhere."""
    head = f"Wordle (terminal) {won_in if won_in else 'X'}/{max_guesses}"
    rows = ["".join(EMOJI[s] for s in scores) for _, scores in history]
    return "\n".join([head, *rows])


# --------------------------------------------------------------------------
# Input
# --------------------------------------------------------------------------

def read_guess(turn: int, max_guesses: int) -> str:
    while True:
        try:
            raw = input(f"\nGuess {turn}/{max_guesses}: ").strip().lower()
        except EOFError:
            print()
            sys.exit("No more input -- goodbye!")
        if len(raw) != WORD_LENGTH:
            print(f"   Please enter exactly {WORD_LENGTH} letters.")
        elif not (raw.isascii() and raw.isalpha()):
            print("   Letters a-z only, please.")
        else:
            return raw


def load_words(path: str) -> list:
    words = set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                w = line.strip().lower()
                if len(w) == WORD_LENGTH and w.isascii() and w.isalpha():
                    words.add(w)
    except OSError as err:
        sys.exit(f"Could not read {path}: {err}")
    if not words:
        sys.exit(f"No {WORD_LENGTH}-letter words found in {path}.")
    return sorted(words)


# --------------------------------------------------------------------------
# One round, and the main loop
# --------------------------------------------------------------------------

def play_round(answer: str, max_guesses: int, color: bool) -> bool:
    """Play a single game; return True if the player found the word."""
    tracker = {c: UNUSED for c in string.ascii_lowercase}
    history = []

    print(f"\nI'm thinking of a {WORD_LENGTH}-letter word. "
          f"You have {max_guesses} guesses.")

    while len(history) < max_guesses:
        guess = read_guess(len(history) + 1, max_guesses)
        scores = score_guess(guess, answer)
        history.append((guess, scores))
        update_tracker(tracker, guess, scores)

        show_board(history, max_guesses, color)
        show_letters(tracker, color)

        if guess == answer:
            n = len(history)
            praise = PRAISE[n - 1] if n <= len(PRAISE) else "Nice!"
            print(f"\n{praise} You got it in {n}/{max_guesses}.\n")
            print(share_grid(history, max_guesses, n))
            return True

    print(f"\nOut of guesses -- the word was {answer.upper()}.\n")
    print(share_grid(history, max_guesses, None))
    return False


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Play Wordle in the terminal.")
    parser.add_argument("--guesses", type=int, default=DEFAULT_GUESSES,
                        metavar="N",
                        help=f"number of guesses allowed (default: {DEFAULT_GUESSES})")
    parser.add_argument("--words", metavar="FILE",
                        help="file of words (one per line) to draw answers from")
    parser.add_argument("--answer", metavar="WORD",
                        help="use WORD as the secret word instead of a random one")
    parser.add_argument("--no-color", action="store_true",
                        help="print plain text instead of colored tiles")
    args = parser.parse_args(argv)

    if args.guesses < 1:
        parser.error("--guesses must be at least 1")

    fixed = None
    if args.answer:
        fixed = args.answer.strip().lower()
        if len(fixed) != WORD_LENGTH or not (fixed.isascii() and fixed.isalpha()):
            parser.error(f"--answer must be a {WORD_LENGTH}-letter word")

    pool = load_words(args.words) if args.words else ANSWERS
    color = not args.no_color
    if os.name == "nt":
        os.system("")   # nudge Windows terminals into interpreting ANSI colors

    print("\nW O R D L E")
    if color:
        print(f"{tile('a', GREEN)} right spot   "
              f"{tile('b', YELLOW)} wrong spot   "
              f"{tile('c', GRAY)} not in word")
    else:
        print("Marks under each guess: G right spot, Y wrong spot, . not in word")

    while True:
        answer = fixed if fixed else random.choice(pool)
        play_round(answer, args.guesses, color)

        if fixed:               # replaying a fixed word would be no fun
            break
        try:
            again = input("\nPlay again? [y/N] ").strip().lower()
        except EOFError:
            break
        if again not in ("y", "yes"):
            break

    print("\nThanks for playing!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except BrokenPipeError:
        sys.exit(0)   # e.g. output piped through `head`
