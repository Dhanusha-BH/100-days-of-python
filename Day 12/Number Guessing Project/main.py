import random
import art
print(art.logo)
number_list =[]
for i in range(1,101):
    number_list.append(i)


def number_guess(chance):
    correct_guess = True
    while correct_guess:
        print(f"You have a {chance} attempts remaining to guess the number.")
        guess = int(input("Make a guess: "))
        if guess < number:
            print("Too low.")
            chance -= 1
            if chance == 0:
                correct_guess = False
                print(f"You have run out of guesses, You lose")
        elif guess > number:
            print("Too high.")
            chance -= 1
            if chance == 0:
                correct_guess = False
                print(f"You have run out of guesses, You lose")
        elif guess == number:
            correct_guess = False
            print(f"You got it! The answer was {number}.")


print("Welcome to the Number Guessing Game!")
print("I'm thinking of a number between 1 and 100.")
number= random.choice(number_list)

difficulty = input("choose a difficulty. Type 'easy' or 'hard':")
if difficulty == 'easy':
    attempt = 10
    number_guess(attempt)
elif difficulty == 'hard':
    attempt = 5
    number_guess(attempt)

