from flask import Flask

app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

import time

def delay_decorator(function):
    def wrapper_function():
        time.sleep(1)
        function()
        function()
    return wrapper_function

@delay_decorator
def say_hello():
    print("Hello")

say_hello()




