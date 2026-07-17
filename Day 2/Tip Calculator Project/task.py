print("Welcome to the tip calculator!")
bill = float(input("What was the total bill? $"))
tip = int(input("What percentage tip would you like to give? 10 12 15 "))
people = int(input("How many people to split the bill? "))
tip_as_percentage = tip / 100
tip_as_amount = bill * tip_as_percentage
total_bill = tip_as_amount + bill
bill_per_person = total_bill / people
final_amount = round(bill_per_person, 2)
print(f"Each person should pay:${final_amount}")




