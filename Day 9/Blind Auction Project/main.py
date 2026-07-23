# TODO-1: Ask the user for input
# TODO-2: Save data into dictionary {name: price}
# TODO-3: Whether if new bids need to be added
# TODO-4: Compare bids in dictionary
import art
print(art.logo)

choice_continue = True
while choice_continue:

    name=input("What is your name?:")
    price = int(input("What is your bid?: $"))
    name_bid=  {}
    name_bid[name] = price
    print("Are there any other bidders? Type 'yes' or 'no':")
    choice = input().lower()
    if choice == "yes":
        print("\n" * 20)
    else:
        choice_continue = False
        high_bid = 0
        winner =""
        for key in name_bid:
            amt = name_bid[key]
            if amt > high_bid:
                high_bid = amt
                winner = key

        print(f"The winner is {winner} with a bid of ${high_bid}.")




