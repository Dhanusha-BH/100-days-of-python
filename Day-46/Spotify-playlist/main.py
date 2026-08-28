import requests
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic,OAuthCredentials
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

url = f"https://appbrewery.github.io/bakeboard-hot-100/{date}"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")
song_names = [tag.getText().strip() for tag in soup.select("h3.chart-entry__title")]
#print(song_names)

client_id = os.getenv("YOUTUBE_CLIENT_ID")
client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
oauth_file = Path(r"C:\Users\Anusha\Desktop\100-days-of-python\oauth.json")
yt = YTMusic(
    str(oauth_file),
    oauth_credentials=OAuthCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
)
print(yt.get_account_info())