import random


def random_move():
    """
    Returns a random move for the computer in a rock-paper-scissors game.
    """

    n = random.randint(1, 3)
    if n == 1:
        return "rock"
    elif n == 2:
        return "paper"
    else:
        return "scissors"


def winner(player, computer):
    if player == computer:
        return "tie"
    elif (
        (player == "rock" and computer == "scissors")
        or (player == "paper" and computer == "rock")
        or (player == "scissors" and computer == "paper")
    ):
        return "player"
    else:
        return "computer"


def play(player):
    computer = random_move()
    print("You chose:     ", player)
    print("Computer chose:", computer)

    result = winner(player, computer)
    if result == "tie":
        print("It's a tie!")
    elif result == "player":
        print("You win!")
    else:
        print("Computer wins!")


player = input("Enter rock, paper, or scissors: ")
play(player)
