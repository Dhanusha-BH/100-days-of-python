from urllib import response

from bs4 import BeautifulSoup
import requests

response= requests.get("https://news.ycombinator.com/")
yc_web_page=response.text

soup=BeautifulSoup(yc_web_page,"html.parser")
articles = soup.find_all("span", class_="titleline")  # see note below on class name

article_texts = []
article_links = []

for article_tag in articles:
    text = article_tag.getText()
    article_texts.append(text)
    link = article_tag.find(name ='a').get("href")
    article_links.append(link)

subtext = soup.find_all(class_="subtext")
article_upvotes = [int(line.span.span.getText().strip(" points")) if line.span.span else 0 for line in subtext]

largest_number = max(article_upvotes)
largest_index = article_upvotes.index(largest_number)


print(
    f"Most upvoted article: {article_texts[largest_index]}\n"
    f"Number of upvotes: {article_upvotes[largest_index]} points\n"
    f"Available at: {article_links[largest_index]}."
)

























# import lxml
#
#
# with open("website.html") as file:
#     content=file.read()
#
# soup = BeautifulSoup(content,"html.parser")
# print(soup.title)
#
# print((soup.a))