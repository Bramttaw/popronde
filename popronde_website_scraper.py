import requests
from bs4 import BeautifulSoup
import csv
import time
import urllib3
import certifi
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pandas as pd

BASE_URL = "https://popronde.nl/archief/"
YEARS = range(2011, 2024)  # up to and including 2023
OUTPUT_FILE = "popronde_artists.csv"

all_artists = []

for year in YEARS:
    url = f"{BASE_URL}{year}"
    print(f"Scraping {url}...")
    response = requests.get(url, verify=certifi.where())

    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    artist_links = soup.find_all("a", class_="artist-link")

    for link in artist_links:
        artist_row = link.find("div", class_="row artist-row")
        if artist_row:
            col8 = artist_row.find("div", class_="col-8")
            col4 = artist_row.find("div", class_="col-4")

            artist = col8.get_text(strip=True) if col8 else None
            genre = col4.get_text(strip=True) if col4 else None

            if artist:
                all_artists.append({
                    "artist": artist,
                    "genre": genre,
                    "year": year
                })

    time.sleep(1)  # Be kind to the server

# Write to CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["artist", "genre", "year"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for artist in all_artists:
        writer.writerow(artist)

print(f"Scraping completed! Data saved to {OUTPUT_FILE}")

df = pd.read_csv(OUTPUT_FILE)