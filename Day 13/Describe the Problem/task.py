def my_function():
    for i in range(1, 20):
        if i == 20:
            print("You got it")


my_function()

# Describe the Problem - Write your answers as comments:
# 1. What is the for loop doing?
# 2. When is the function meant to print "You got it"?
# 3. What are your assumptions about the value of i?

# for loop is looping through only between 1 and 19  so i value never becomes 20 so it didn't print anything
# when we include 20 in range that is for i in range(1,21) in the last iteration i becomes 20 and the if statement gets executed

def my_function():
    for i in range (1,21):
        if i == 20:
            print("You got it")

my_function()