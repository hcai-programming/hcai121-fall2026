# Please create a version of Wordle in Python.  This is the guess 5-letter word game that gives hints as follows: Letters in the correct spot are labeled green, correct letters in the wrong spot are labeled yellow, and letters not in the word labeled gray.   There should be at most 6 guesses (but that  should be something that can be changed).

import random


class Wordle:
    def __init__(self, word_list, max_guesses=6):
        self.word_list = word_list
        self.max_guesses = max_guesses
        self.target_word = random.choice(word_list)
        self.guesses = []

    def guess(self, word):
        if len(word) != 5 or word not in self.word_list:
            raise ValueError("Invalid guess. Please enter a valid 5-letter word.")

        self.guesses.append(word)
        feedback = self.get_feedback(word)
        return feedback

    def get_feedback(self, guess):
        feedback = []
        for i in range(5):
            if guess[i] == self.target_word[i]:
                feedback.append("green")  # Correct letter and position
            elif guess[i] in self.target_word:
                feedback.append("yellow")  # Correct letter but wrong position
            else:
                feedback.append("gray")  # Letter not in the word
        return feedback

    def is_game_over(self):
        return (
            len(self.guesses) >= self.max_guesses
            or self.guesses[-1] == self.target_word
        )

    def get_target_word(self):
        return self.target_word


# Example usage:
if __name__ == "__main__":
    word_list = ["apple", "grape", "peach", "berry", "melon"]
    game = Wordle(word_list)

    print("Welcome to Wordle!")
    print(f"You have {game.max_guesses} guesses to find the 5-letter word.")

    while not game.is_game_over():
        guess = input("Enter your guess: ").lower()
        try:
            feedback = game.guess(guess)
            print("Feedback:", feedback)
        except ValueError as e:
            print(e)

    if game.guesses[-1] == game.get_target_word():
        print("Congratulations! You've guessed the word:", game.get_target_word())
    else:
        print("Game over! The correct word was:", game.get_target_word())
