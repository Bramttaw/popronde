import requests
from bs4 import BeautifulSoup
import csv
import time
import urllib3
import certifi
import re
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
    
    # Find the section containing artist names and genres
    # Look for the header with text "Artiesten {year}"
    header = soup.find(lambda tag: tag.name == "h2" and f"Artiesten {year}" in tag.text)
    if not header:
        print(f"Could not find the 'Artiesten {year}' section in {url}")
        continue

    # The artist information is typically in the next sibling after the header
    artist_section = header.find_next_sibling()
    if not artist_section:
        print(f"Could not find artist section after header in {url}")
        continue

    # Extract text from the artist section
    artist_text = artist_section.get_text(separator="\n")
    lines = artist_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        # Use regex to split the line into artist name and genre
        match = re.match(r"^(.*?)\s+([A-Za-z &/]+)$", line)
        if match:
            name = match.group(1).strip()
            genre = match.group(2).strip()
            all_artists.append({
                "artist": name,
                "genre": genre,
                "year": year
            })
        else:
            print(f"Could not parse line: '{line}' in year {year}")
    
    time.sleep(1)  # be kind to the server

# Write to CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["artist", "genre", "year"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for artist in all_artists:
        writer.writerow(artist)

print(f"Scraping completed! Data saved to {OUTPUT_FILE}")