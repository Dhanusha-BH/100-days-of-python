import art
def add(n1, n2):
    return n1 + n2

def subtract(n1, n2):
    return n1 - n2

def multiply(n1, n2):
    return n1 * n2

def divide(n1, n2):
    return n1 / n2

operation = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
}
def calculator():
    print(art.logo)
    first_number = float(input("What's your first number?:"))
    should_continue = True

    while should_continue:
        for symbol in operation:
            print(symbol)
        operation_choice = input("Pick an operation: ")
        second_number = float(input("What's your second number?:"))

        result = operation[operation_choice](first_number, second_number)
        print(f"{first_number} {operation_choice} {second_number} = {result}")

        second_chioce= input(f"Type 'y' to continue calculating with {result}, or type 'n' to start a new calculation: ").lower()

        if second_chioce == "y":
            first_number = result

        else:
            should_continue = False
            print("\n" * 100)
            calculator()


calculator()




