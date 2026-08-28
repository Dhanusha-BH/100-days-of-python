# from flask import Flask
#
# app = Flask(__name__)
#
# @app.route('/')
# def hello_world():
#     return '<h1 style="text-align:center">Hello World!</h1>'\
#     '<p>This is a paragraph.</p>'\
#     '<img src="https://giphy.com/gifs/cat-kitten-cute-3z3Jqt42yS104gRc5c">'
# @app.route("/<name>/<int:number>")
# def greet(name,number):
#     return f"Hello, {name} you are {number} old!"
#
# if __name__ == '__main__':
#     app.run(debug=True)

class User:
    def __init__(self,name):
        self.name = name
        self.is_logged_in = False


def is_authenticated_decorator(function):
    def wrapper(*args, **kwargs):
        if args[0].is_logged_in == True:
            function(args[0])
    return wrapper

@is_authenticated_decorator
def create_blog_post(user):
    print(f"This is {user.name}'s new blog post.")

new_user = User("Dhanusha")
new_user.is_logged_in = True
create_blog_post(new_user)