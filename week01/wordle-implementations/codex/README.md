# Python Wordle

A dependency-free terminal version of the five-letter guessing game. Letters in
the right position are green, letters elsewhere in the word are yellow, and
letters not in the word are gray. Repeated letters are scored correctly.

## Play

Python 3.10 or newer is recommended.

```bash
python3 wordle.py
```

The default limit is six guesses. Change it from the command line:

```bash
python3 wordle.py --max-guesses 8
```

Useful options:

```bash
# Choose the answer (useful for a classroom demonstration)
python3 wordle.py --secret apple

# Use explicit GREEN/YELLOW/GRAY labels if colored symbols do not display well
python3 wordle.py --plain
```

Guesses must be exactly five English letters. They do not have to be in the
bundled answer list, so the game does not reject legitimate words that are not
included in its compact dictionary.

## Test

```bash
python3 -m unittest -v
```

The default can also be changed in `wordle.py` by editing
`DEFAULT_MAX_GUESSES`.
