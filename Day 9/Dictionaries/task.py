programming_dictionary = {"Bug": "An error in a program that prevents the program from running as expected.", "Function": "A piece of code that you can easily call over and over again."}

print(programming_dictionary)

print(programming_dictionary["Bug"])

programming_dictionary["loop"]="do the action over and over again"
print(programming_dictionary)

for key in programming_dictionary:
    print(key)
    print(programming_dictionary[key])

empty_dictionary = {}
print(empty_dictionary)

student_scores = {
    'Harry': 88,
    'Ron': 78,
    'Hermione': 95,
    'Draco': 75,
    'Neville': 60
}
student_grades = {}

for key in student_scores:
    name = key
    score = student_scores[key]
    if  score >= 91 and score <= 100:
        student_grades[key] = "Outstanding"

print(student_grades)