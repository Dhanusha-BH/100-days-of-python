#def greet(name,course):
    #print(f"Hello {name}")
    #print(f"Which course are you studying?: {course}")

# greet("Dhanusha" ,"Python") this is a positional argument
#greet(name="Dhanusha",course="Python") # this is the keyword argument




def calculate_love_score(name1,name2):
    letter_T = 0
    letter_R = 0
    letter_U = 0
    letter_E = 0
    total_true_name1 = 0
    for letter in name1:
        if letter == "T" or letter == "t":
            letter_T += 1
        elif letter == "R" or letter == "r":
            letter_R += 1
        elif letter == "U" or letter == "u":
            letter_U += 1
        elif letter == "E" or letter == "e":
            letter_E += 1
    total_true_name1 = letter_T + letter_R + letter_U + letter_E
    #print(total_true_name1)

    total_true_name2 = 0
    letter_T = 0
    letter_R = 0
    letter_U = 0
    letter_E = 0

    for letter in name2:
        if letter == "T" or letter == "t":
            letter_T += 1
        elif letter == "R" or letter == "r":
            letter_R += 1
        elif letter == "U" or letter == "u":
            letter_U += 1
        elif letter == "E" or letter == "e":
            letter_E += 1

    total_true_name2 = letter_T + letter_R + letter_U + letter_E
    #print(total_true_name2)
    total_1=str(total_true_name1+total_true_name2)

    letter_L = 0
    letter_O = 0
    letter_V = 0
    letter_E = 0
    total_love_name1= 0
    for letter in name1:
        if letter == "L" or letter == "l":
            letter_L +=  1
        elif letter == "O" or letter == "o":
            letter_O +=  1
        elif letter == "V" or letter == "v":
            letter_V +=  1
        elif letter == "E" or letter == "e":
            letter_E +=  1
    total_love_name1 = letter_L + letter_O + letter_V + letter_E
    #print(total_love_name1)

    letter_L = 0
    letter_O = 0
    letter_V = 0
    letter_E = 0
    total_love_name2 = 0
    for letter in name2:
        if letter == "L" or letter == "l":
            letter_L +=  1
        elif letter == "O" or letter == "o":
            letter_O +=  1
        elif letter == "V" or letter == "v":
            letter_V +=  1
        elif letter == "E" or letter == "e":
            letter_E += 1

    total_love_name2 = letter_L + letter_O + letter_V + letter_E
   # print(total_love_name2)
    total_2=str(total_love_name1+total_love_name2)
    print(total_1+total_2)



calculate_love_score(name1 = "Angela Yu" ,name2 = "Jack Bauer")