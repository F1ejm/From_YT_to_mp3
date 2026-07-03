from bs4 import BeautifulSoup
import requests

page = requests.get("https://toscrape.com")
soup = BeautifulSoup(page.text, "html.parser")

nwm = soup.findAll("div", class_="col-md-6")

print(nwm)
