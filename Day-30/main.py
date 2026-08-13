#File not found

#try:
#    file = open("a_file.txt")
#    a_dictionary = {"Key": "Value"}
#    print(a_dictionary["Key"])
#except FileNotFoundError:
#    file=open("a_file.txt", "w")
#    file.write("Something")
#except KeyError as error_message:
#    print(f"The key {error_message} does not exist")
#else:
#    content=file.read()
#    print(content)
#finally:
#    file.close()
#    print("The file has been closed")

height = float(input("Enter the Height: "))
weight = int(input("Enter the weight: "))

if height > 3:
    raise ValueError("Human Height should not be over 3 meters.")

bmi = weight / (height ** 2)
print(f"BMI: {bmi}")