from fastapi import FastAPI
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from dotenv import load_dotenv
import os
import authentication as auth

load_dotenv()

app = FastAPI()


sp_oauth = SpotifyOAuth(
    client_id=auth.client_id,
    client_secret=auth.client_secret,
    redirect_uri='https://www.google.com/',
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
