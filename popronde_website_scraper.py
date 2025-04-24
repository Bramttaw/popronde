import requests
from bs4 import BeautifulSoup
import csv
import time
import urllib3
import certifi
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    
    # Look for artist blocks
    artist_blocks = soup.find_all("div", class_="row artiesten__row")

    for block in artist_blocks:
        try:
            name = block.find("p", class_="artiesten__name").text.strip()
            genre = block.find("p", class_="artiesten__genre").text.strip()
        except AttributeError:
            # Skip blocks that don't follow the expected structure
            continue
        
        all_artists.append({
            "artist": name,
            "genre": genre,
            "year": year
        })

    time.sleep(1)  # be kind to the server

# Write to CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["artist", "genre", "year"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for artist in all_artists:
        writer.writerow(artist)

print(f"Scraping completed! Data saved to {OUTPUT_FILE}")
