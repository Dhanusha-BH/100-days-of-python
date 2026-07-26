import art
import game_data
import random

print(art.logo)
score = 0
account_B = random.choice(game_data.data)

def format_data(account):
    account_name = account["name"]
    account_description = account["description"]
    account_country = account["country"]
    return f"{account_name}, a {account_description},  from {account_country}"

def check_answer(user_choice,a_followers,b_followers):
    if a_followers > b_followers:
        return user_choice == 'a'
    else:
        return user_choice == 'b'

game_should_continue = True

while game_should_continue:
    account_A = account_B
    account_B = random.choice(game_data.data)
    if account_A == account_B:
        account_B = random.choice(game_data.data)

    print(f"Compare A: {format_data(account_A)}")
    print(art.vs)
    print(f"Against B: {format_data(account_B)}")

    user_guess = input("who has more followers? Type 'A' or 'B': ").lower()

    print("\n"*20)
    print(art.logo)

    a_followers_count = account_A["follower_count"]
    b_followers_count = account_B["follower_count"]
    is_correct = check_answer(user_guess, a_followers_count, b_followers_count)

    if is_correct:
        score += 1
        print(f"You're right! current score: {score}")
    else:
        print(f"Sorry, that's wrong. Final score: {score}")
        game_should_continue = False
















