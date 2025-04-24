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

results = []

def spotify_popularity(artists_df):

    # Load festival artist CSV (columns: artist, year, shows)
    df_artists = artists_df

    

    for _, row in tqdm(df_artists.iterrows(), total=len(df_artists), desc="Processing artists"):
        artist_name = row["artist"]
        festival_year = int(row["year"])

        try:
            # Search for artist
            search_result = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
            items = search_result["artists"]["items"]
            if not items:
                continue
            artist_id = items[0]["id"]

            # Get albums
            album_results = sp.artist_albums(artist_id, album_type="album", limit=50)
            albums = {}
            seen = set()

            for album in album_results["items"]:
                name = album["name"]
                if name.lower() in seen:
                    continue
                seen.add(name.lower())

                try:
                    year = int(album["release_date"][:4])
                except:
                    continue

                album_id = album["id"]
                tracks = sp.album_tracks(album_id)
                track_ids = [t["id"] for t in tracks["items"]]

                if not track_ids:
                    continue

                # Get track popularity
                total_popularity = 0
                for i in range(0, len(track_ids), 50):
                    track_batch = sp.tracks(track_ids[i:i+50])
                    for t in track_batch["tracks"]:
                        total_popularity += t.get("popularity", 0)

                albums[year] = albums.get(year, []) + [{
                    "name": name,
                    "popularity": total_popularity
                }]

            if not albums:
                continue  # skip artist with no albums at all

            # Sort albums
            all_albums = []
            for y in sorted(albums.keys()):
                for a in albums[y]:
                    all_albums.append({
                        "year": y,
                        "name": a["name"],
                        "popularity": a["popularity"]
                    })

            # Find album closest to festival year
            during_album = None
            for album in all_albums:
                if album["year"] == festival_year:
                    during_album = album
                    break

            # Get index of "anchor" year for album sorting
            if during_album:
                idx = all_albums.index(during_album)
            else:
                # Use year index of album closest to the festival year (for ordering)
                idx = min(range(len(all_albums)), key=lambda i: abs(all_albums[i]["year"] - festival_year))

            row_out = {
                "artist": artist_name,
                "festival_year": festival_year,
                "album_name": all_albums[idx]["name"] if during_album else None,
                "p_album_2before": all_albums[idx-2]["popularity"] if idx >= 2 else None,
                "p_album_1before": all_albums[idx-1]["popularity"] if idx >= 1 else None,
                "p_album_during": during_album["popularity"] if during_album else None,
                "p_album_1after": all_albums[idx+1]["popularity"] if idx + 1 < len(all_albums) else None,
                "p_album_2after": all_albums[idx+2]["popularity"] if idx + 2 < len(all_albums) else None,
            }

            results.append(row_out)

        except Exception as e:
            print(f"Error processing {artist_name}: {e}")
            continue

    # Build final dataframe
    df_result = pd.DataFrame(results)
    df_result.to_csv("artist_album_popularity_full.csv", index=False)
    print("✅ Done! Saved to artist_album_popularity_full.csv")
    return df_result