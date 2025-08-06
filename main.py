from dotenv import load_dotenv
import os
import base64
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time



load_dotenv(dotenv_path=".env")



client_id=os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")


scope="user-library-read"
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

last_saved_tracks=set()

results=sp.current_user_saved_tracks(limit=50)
for items in results['items']:    
    track_id=items['track']['id']
    last_saved_tracks.add(track_id)

print("monitoring for new liked songs...")

while True:
    try:
        current_results=sp.current_user_saved_tracks(limit=50)
        current_saved_tracks=set()

        for item in current_results['items']:
            track_id=item['track']['id']
            current_saved_tracks.add(track_id)

            if track_id not in last_saved_tracks:
                track_name=item['track']['name']
                artist_name=item['track']['artists'][0]['name']

                print(f"🎵 NEW LIKED SONG: {track_name} by {artist_name}")
        
        last_saved_tracks=current_saved_tracks
        time.sleep(30)
    except Exception as e:
      print(f"Error: {e}")
      time.sleep(60)
