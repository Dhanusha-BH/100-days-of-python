#List comprehension
name ="Dhanusha"
new_list = [letter for letter in name]
#print(new_list)


new_number =[i*2 for i in range(1,5)]
#print(new_number)

names =["Dhanusha","Alex","Beth","Dave","Freddie"]

names_list = [name.upper() for name in names if len(name) > 5]
#print(names_list)

list_of_strings = ['9', '0', '32', '8', '2', '8', '64', '29', '42', '99']
numbers =  [int(num) for num in list_of_strings]
#print(numbers)

#Dictionary Comprehension
#new_dict ={new_key:new_value for (key,value) in dict.items() if test}

import random

student_score = {student:random.randint(1,100) for student in names}
#print(student_score)

passed_students = {student:score for (student, score) in student_score.items() if score >= 55}
#print(passed_students)

sentence = "What is the Airspeed Velocity of an Unladen Swallow?"
word_list= sentence.split()
result = {word:len(word) for word in word_list}
#print(result)


import pandas

student_dict = {
    "student": ["Angela","Dhanusha","James","Lilly"],
    "score": [45,67,89,78]
}

student_data_frame = pandas.DataFrame(student_dict)
print(student_data_frame)

#loop through a data frame
#for (key,value) in student_data_frame.items():
#    print(value)

#llop through rows of a data frame
for (index,row) in student_data_frame.iterrows():
    print(row.score)