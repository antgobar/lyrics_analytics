import requests
from bs4 import BeautifulSoup

lyrics_url = "https://genius.com/Sia-chandelier-lyrics"

page = requests.get(lyrics_url)

soup = BeautifulSoup(page.content, "html.parser")
