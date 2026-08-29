from flask import Flask, render_template
import random
import datetime
import requests

app = Flask(__name__)

@app.route('/')
def home():
    random_number = random.randint(1, 10)
    current_year = datetime.datetime.now().year

    return render_template("index.html",number = random_number,year = current_year)

@app.route('/guess/<name>')
def guess(name):
    gender_url =f"https://api.genderize.io?name={name}"
    response = requests.get(gender_url)
    gender_data = response.json()
    gender=gender_data["gender"]
    age_url = f"https://api.agify.io?name={name}"
    response = requests.get(age_url)
    age_data = response.json()
    age=age_data["age"]
    return render_template("guess.html",name = name,gender = gender,age = age)

@app.route('/blog')
def get_blog():
    blog_url ="https://api.npoint.io/c790b4d5cab58020d391"
    response = requests.get(blog_url)
    blog_data = response.json()
    return render_template("blog.html",blog = blog_data)

if __name__ == '__main__':
    app.run(debug=True)