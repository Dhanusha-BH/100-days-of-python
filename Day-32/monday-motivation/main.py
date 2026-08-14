import smtplib
import datetime as dt
import random
from multiprocessing import connection
my_email= "bhdhanusha@gmail.com"
my_password = "hlmhwuwmwaqeczge"

now = dt.datetime.now()
weekday = now.weekday()
if weekday == 0:
    with open("quotes.txt") as quote_file:
        all_quotes = quote_file.readlines()
        quote = random.choice(all_quotes)

    print(quote)

    with  smtplib.SMTP('smtp.gmail.com', 587) as connection:
        connection.starttls()
        connection.login(my_email, my_password)
        connection.sendmail(
            from_addr=my_email,
            to_addrs=my_email,
            msg=f"Subject:Monday Motivation!\n\n{quote}"
        )



