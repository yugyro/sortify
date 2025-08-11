from dotenv import load_dotenv
import os
import base64
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import pylast
import re



load_dotenv(dotenv_path=".env")

# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from https://www.last.fm/api/account/create for Last.fm
API_KEY = os.getenv("LAST_FM_API_KEY")
API_SECRET = os.getenv("LAST_FM_SHARED_SECRET")
LAST_FM_USERNAME=os.getenv("LAST_FM_USERNAME")


network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=LAST_FM_USERNAME
)

client_id=os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")


scope="user-library-read playlist-modify-public playlist-modify-private"
       
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

"""""
JSON object → Python dict
JSON array → Python list
JSON string → Python str
JSON number → Python int or float
"""
def load_playlists_map(path="genre_playlists.json"):
    with open(path,"r") as f:                                           #helper function 1 (loading map from json file)
        return json.load(f)                                              

def get_playlist(genre,mappings):                                       #helper function 2 (get playlist url from map)
    return mappings.get(genre.lower())

synonyms={
        "rap" : "hip-hop",
        "hip hop":"hip-hop",
        "hiphop":"hip-hop",
        "kanye west":"hip-hop",
        "trap":"hip-hop",

        "sophisti-pop": "r&b",
        "neo-soul":"r&b",
        "olivia" : "r&b",
        "rnb":"r&b",
        "art pop":"r&b",
        "soul":"r&b",
        "alternative rnb":"r&b",
        "pop":"r&b",
        "indie":"r&b",
        "indie pop":"r&b",
        "drake":"r&b",
        "partynextdoor":"r&b",

        "hard rock":"rock",
        "classic rock":"rock",
        "80's":"rock"
}
def parse_tag(tags):
    tag_nonum=re.sub(r"\s+\d+$","",tags)

    clean_tag=tag_nonum.strip().lower()
    return clean_tag
def normalize_tag(tag):
    tag=parse_tag(tag)
    return synonyms.get(tag,tag)

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

                lastfmtrack=network.get_track(artist_name,track_name)
                if lastfmtrack:
                    print("Track recieved")
                else:
                    print("track reception error")
                tags=lastfmtrack.get_top_tags()[:4]
                playlist_map=load_playlists_map()
                for tag in tags :
                    if tag:
                        normalized_tag=normalize_tag(tag.item.name)
                        print(normalized_tag,tag.weight)
                        if(normalized_tag in playlist_map):
                            playlist_url=get_playlist(normalized_tag,playlist_map)
                            if(playlist_url):
                                track_uri=f"spotify:track:{track_id}"
                                sp.playlist_add_items(playlist_url,[track_uri])
                                print(f"added {track_name} to playlist {normalized_tag}")
                            else:
                                print("invalid playlist url")
                        else:
                            print(f"{normalized_tag} playlist not available, moving to next tag")
                    else:
                        print("coudnt obtain tags")

        last_saved_tracks=current_saved_tracks
        time.sleep(30)
    except Exception as e:
      print(f"Error: {e}")
      time.sleep(60)
