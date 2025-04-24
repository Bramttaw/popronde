import os
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import authentication as auth

load_dotenv()

# app = FastAPI()

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=auth.client_id,
    client_secret=auth.client_secret,
))

# Load CSV with artist names
csv_path = "artists.csv"  # Change if needed
df_input = pd.read_csv(csv_path)

# Make sure column exists
if "artist" not in df_input.columns:
    raise ValueError("CSV must contain a column named 'artist'")

# Prepare output
data = []

for name in tqdm(df_input["artist"], desc="Processing artists"):
    try:
        # Search for artist
        result = sp.search(q=f"artist:{name}", type="artist", limit=1)
        items = result["artists"]["items"]
        if not items:
            continue

        artist = items[0]
        artist_id = artist["id"]
        genres = artist.get("genres", [])
        popularity = artist.get("popularity", 0)

        # Get albums
        albums = sp.artist_albums(artist_id, album_type="album,single", limit=50)
        album_ids = list({album["id"] for album in albums["items"]})
        num_albums = len(album_ids)

        # Count tracks
        num_tracks = 0
        for album_id in album_ids:
            tracks = sp.album_tracks(album_id)
            num_tracks += len(tracks["items"])

        data.append({
            "artist_name": artist["name"],
            "genres": ", ".join(genres),
            "popularity": popularity,
            "num_albums": num_albums,
            "num_tracks": num_tracks
        })

    except Exception as e:
        print(f"Error processing {name}: {e}")

# Final DataFrame
df_output = pd.DataFrame(data)
df_output.to_csv("spotify_artist_data_output.csv", index=False)
print("✅ Done! Saved to spotify_artist_data_output.csv")


# @app.get("/")
# def root():
#     return {"message": "Welcome to the Spotify API"}

# @app.get("/me")
# def get_user_profile():
#     return sp.current_user()

# @app.get("/tracks/{track_id}")
# def get_track(track_id: str):
#     return sp.track(track_id)
