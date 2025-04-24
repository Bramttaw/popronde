from fastapi import FastAPI
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-library-read"
)

token_info = sp_oauth.get_access_token(as_dict=False)
sp = Spotify(auth=token_info)

@app.get("/")
def root():
    return {"message": "Welcome to the Spotify API"}

@app.get("/me")
def get_user_profile():
    return sp.current_user()

@app.get("/tracks/{track_id}")
def get_track(track_id: str):
    return sp.track(track_id)
