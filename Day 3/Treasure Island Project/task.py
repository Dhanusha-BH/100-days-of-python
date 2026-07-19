print(r'''
*******************************************************************************
          |                   |                  |                     |
 _________|________________.=""_;=.______________|_____________________|_______
|                   |  ,-"_,=""     `"=.|                  |
|___________________|__"=._o`"-._        `"=.______________|___________________
          |                `"=._o`"=._      _`"=._                     |
 _________|_____________________:=._o "=._."_.-="'"=.__________________|_______
|                   |    __.--" , ; `"=._o." ,-"""-._ ".   |
|___________________|_._"  ,. .` ` `` ,  `"-._"-._   ". '__|___________________
          |           |o`"=._` , "` `; .". ,  "-._"-._; ;              |
 _________|___________| ;`-.o`"=._; ." ` '`."\ ` . "-._ /_______________|_______
|                   | |o ;    `"-.o`"=._``  '` " ,__.--o;   |
|___________________|_| ;     (#) `-.o `"=.`_.--"_o.-; ;___|___________________
____/______/______/___|o;._    "      `".o|o_.--"    ;o;____/______/______/____
/______/______/______/_"=._o--._        ; | ;        ; ;/______/______/______/_
____/______/______/______/__"=._o--._   ;o|o;     _._;o;____/______/______/____
/______/______/______/______/____"=._o._; | ;_.--"o.--"_/______/______/______/_
____/______/______/______/______/_____"=.o|o_.--""___/______/______/______/____
/______/______/______/______/______/______/______/______/______/______/_____ /
*******************************************************************************
''')
print("Welcome to Treasure Island.")
print("Your mission is to find the treasure.")

direction= input("Your at crossroad where do you want to go? "
                 "Type Left or Right\n").lower()
if direction == "left":
    print("You arrive at the island you can Swim or Wait ")
    action = input("Choose your action: Swim or Wait\n").lower()
    if action ==  "wait":
        print("You are near at  the treasure ,"
              "Which door do you want to go? "
              "Red ,Yellow or Blue ")
        door = input("Choose you door\n").lower()
        if door == "yellow":
            print("You got the treasure , You Win")
        elif door == "red":
            print("You eaten by the beats , Game Over")
        elif door ==  "blue":
            print("Burned by the fire, Game over")
        else:
            print("Sorry you have to choose between those three doors, "
                  "Game over")
    else:
        print("Island is so big you are not allowed to swim, "
              "Game Over ")
else:
    print("You  are blocked by the loin you can't go further: "
          "Game over")



