"""A small, dependency-free Wordle-style terminal game."""

from __future__ import annotations

import argparse
import random
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence


WORD_LENGTH = 5
DEFAULT_MAX_GUESSES = 6

# A compact list keeps the project self-contained. Guesses do not have to appear
# in this list; it is only used to choose the secret word.
WORDS = (
    "about", "above", "actor", "acute", "admit", "adopt", "after", "again",
    "agent", "agree", "ahead", "alarm", "album", "alert", "alien", "align",
    "alive", "allow", "alone", "along", "alter", "amber", "ample", "angel",
    "apple", "apply", "arena", "argue", "arise", "arrow", "aside", "audio",
    "avoid", "award", "aware", "baker", "beach", "began", "begin", "below",
    "bench", "berry", "birth", "black", "blade", "blame", "blank", "blast",
    "blend", "blind", "block", "blood", "board", "boost", "brain", "brave",
    "bread", "break", "brick", "brief", "bring", "broad", "brown", "build",
    "buyer", "cable", "carry", "catch", "cause", "chain", "chair", "charm",
    "chart", "chase", "cheap", "check", "chest", "chief", "child", "claim",
    "class", "clean", "clear", "clerk", "click", "clock", "close", "cloud",
    "coach", "coast", "color", "could", "count", "court", "cover", "craft",
    "crash", "cream", "crime", "cross", "crowd", "crown", "curve", "cycle",
    "daily", "dance", "death", "delay", "depth", "digit", "doubt", "dozen",
    "draft", "drama", "dream", "dress", "drink", "drive", "eager", "early",
    "earth", "eight", "elite", "empty", "enemy", "enjoy", "enter", "entry",
    "equal", "error", "event", "every", "exact", "exist", "extra", "faith",
    "false", "fault", "field", "fifth", "fight", "final", "first", "flame",
    "flash", "fleet", "floor", "focus", "force", "frame", "fresh", "front",
    "fruit", "giant", "given", "glass", "globe", "glory", "grace", "grade",
    "grain", "grand", "grant", "grass", "great", "green", "group", "guard",
    "guess", "guest", "guide", "happy", "heart", "heavy", "horse", "hotel",
    "house", "human", "ideal", "image", "index", "inner", "input", "issue",
    "joint", "judge", "known", "label", "large", "laser", "later", "learn",
    "least", "leave", "legal", "level", "light", "limit", "local", "logic",
    "lucky", "lunch", "major", "maker", "march", "match", "mayor", "metal",
    "might", "minor", "model", "money", "month", "motor", "mount", "mouse",
    "movie", "music", "night", "noise", "north", "novel", "nurse", "occur",
    "ocean", "offer", "often", "order", "other", "owner", "paint", "panel",
    "paper", "party", "peace", "phase", "phone", "photo", "piece", "pilot",
    "pitch", "place", "plain", "plane", "plant", "plate", "point", "pound",
    "power", "press", "price", "pride", "prime", "print", "prize", "proof",
    "proud", "queen", "quick", "quiet", "quite", "radio", "raise", "range",
    "rapid", "reach", "ready", "reply", "right", "rival", "river", "rough",
    "round", "route", "royal", "rural", "scale", "scene", "scope", "score",
    "sense", "serve", "seven", "shade", "shake", "shape", "share", "sharp",
    "sheet", "shelf", "shell", "shift", "shine", "shirt", "shock", "short",
    "sight", "skill", "sleep", "small", "smart", "smile", "solid", "solve",
    "sorry", "sound", "south", "space", "spare", "speak", "speed", "spend",
    "spite", "split", "sport", "staff", "stage", "stake", "stand", "start",
    "state", "steam", "steel", "stick", "still", "stock", "stone", "store",
    "storm", "story", "strip", "study", "style", "sugar", "table", "taste",
    "teach", "thank", "their", "theme", "there", "thick", "thing", "think",
    "third", "those", "three", "throw", "tight", "title", "today", "topic",
    "total", "touch", "tough", "tower", "track", "trade", "train", "treat",
    "trend", "trial", "trust", "truth", "twice", "under", "union", "unity",
    "until", "upper", "urban", "usual", "value", "video", "visit", "vital",
    "voice", "waste", "watch", "water", "wheel", "where", "which", "while",
    "white", "whole", "whose", "woman", "world", "worry", "worth", "would",
    "write", "wrong", "young", "youth",
)


class Mark(Enum):
    """The hint assigned to one guessed letter."""

    CORRECT = "green"
    PRESENT = "yellow"
    ABSENT = "gray"


@dataclass(frozen=True)
class LetterHint:
    letter: str
    mark: Mark


def score_guess(secret: str, guess: str) -> list[LetterHint]:
    """Score *guess* against *secret*, accounting for repeated letters.

    Exact matches are claimed first. Remaining letters can be marked yellow only
    as many times as they remain in the secret word.
    """

    secret = secret.lower()
    guess = guess.lower()
    if len(secret) != len(guess):
        raise ValueError("Secret and guess must have the same length.")

    marks: list[Mark | None] = [None] * len(secret)
    unmatched = Counter()

    for index, (answer_letter, guessed_letter) in enumerate(zip(secret, guess)):
        if answer_letter == guessed_letter:
            marks[index] = Mark.CORRECT
        else:
            unmatched[answer_letter] += 1

    for index, guessed_letter in enumerate(guess):
        if marks[index] is not None:
            continue
        if unmatched[guessed_letter] > 0:
            marks[index] = Mark.PRESENT
            unmatched[guessed_letter] -= 1
        else:
            marks[index] = Mark.ABSENT

    return [LetterHint(letter.upper(), mark) for letter, mark in zip(guess, marks)]  # type: ignore[arg-type]


def format_hints(hints: Sequence[LetterHint], *, plain: bool = False) -> str:
    """Turn scored letters into a terminal-friendly board row."""

    if plain:
        return " ".join(f"[{hint.mark.value.upper()} {hint.letter}]" for hint in hints)

    squares = {
        Mark.CORRECT: "🟩",
        Mark.PRESENT: "🟨",
        Mark.ABSENT: "⬛",
    }
    return " ".join(f"{squares[hint.mark]}{hint.letter}" for hint in hints)


def validate_guess(raw_guess: str, word_length: int = WORD_LENGTH) -> tuple[str | None, str | None]:
    """Return a normalized guess and no error, or no guess and an error."""

    guess = raw_guess.strip().lower()
    if len(guess) != word_length:
        return None, f"Please enter exactly {word_length} letters."
    if not guess.isascii() or not guess.isalpha():
        return None, "Please use letters A-Z only."
    return guess, None


def play_game(
    secret: str,
    max_guesses: int = DEFAULT_MAX_GUESSES,
    *,
    plain: bool = False,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> bool:
    """Play one game. Return True on a win and False on a loss."""

    secret = secret.lower()
    if len(secret) != WORD_LENGTH or not secret.isascii() or not secret.isalpha():
        raise ValueError(f"The secret must contain exactly {WORD_LENGTH} letters A-Z.")
    if max_guesses < 1:
        raise ValueError("max_guesses must be at least 1.")

    output_fn("\nWORDLE")
    output_fn(f"Guess the {WORD_LENGTH}-letter word. You have {max_guesses} guesses.")
    output_fn("Green = right spot | Yellow = wrong spot | Gray = not in word\n")

    guesses_used = 0
    while guesses_used < max_guesses:
        remaining = max_guesses - guesses_used
        try:
            raw_guess = input_fn(f"Guess {guesses_used + 1}/{max_guesses} ({remaining} left): ")
        except (EOFError, KeyboardInterrupt):
            output_fn("\nGame ended.")
            return False

        guess, error = validate_guess(raw_guess)
        if error:
            output_fn(error)
            continue

        guesses_used += 1
        hints = score_guess(secret, guess)  # type: ignore[arg-type]
        output_fn(format_hints(hints, plain=plain))

        if guess == secret:
            noun = "guess" if guesses_used == 1 else "guesses"
            output_fn(f"\nYou won in {guesses_used} {noun}!")
            return True

    output_fn(f"\nOut of guesses. The word was {secret.upper()}.")
    return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Play a Wordle-style word game.")
    parser.add_argument(
        "-m", "--max-guesses",
        type=int,
        default=DEFAULT_MAX_GUESSES,
        help=f"number of guesses allowed (default: {DEFAULT_MAX_GUESSES})",
    )
    parser.add_argument(
        "--secret",
        metavar="WORD",
        help="use a specific secret word (handy for classrooms and testing)",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="show text labels instead of colored square symbols",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.max_guesses < 1:
        parser.error("--max-guesses must be at least 1")

    secret = args.secret.lower() if args.secret else random.choice(WORDS)
    if len(secret) != WORD_LENGTH or not secret.isascii() or not secret.isalpha():
        parser.error(f"--secret must be exactly {WORD_LENGTH} letters A-Z")

    play_game(secret, args.max_guesses, plain=args.plain)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
