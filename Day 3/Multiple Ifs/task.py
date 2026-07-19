print("Welcome to the rollercoaster!")
height = int(input("What is your height in cm? "))
bill = 0

if height >= 120:
    print("You can ride the rollercoaster")
    age = int(input("What is your age? "))
    if age <= 12:
        bill = 5
        print("child ticket are $5.")
    elif age <= 18:
        bill =7
        print("Youth ticket are $7.")
    else:
        bill =12
        print("Adult ticket are $12.")
    wants_photo = input("Would you like to take a photo? Type y for yes or n for no:")
    if wants_photo == "y":
        bill += 3

    print(f"Your total bill is ${bill}")

else:
    print("Sorry you have to grow taller before you can ride.")
