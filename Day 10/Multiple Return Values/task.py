def format_name(f_name, l_name):
    if f_name == "" and l_name == "":
        return "You have not provided valid input"
    formated_f_name = f_name.title()
    formated_l_name = l_name.title()
    return f"{formated_f_name} {formated_l_name}"


print(format_name(input("What's your first name?"),input("What's your last name?")))
