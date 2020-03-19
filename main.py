"""
Tools
- Spotify Web API
- Instagram API?

Steps:
- Login to Instagram using my account
- Access the Stories of the users I follow
- Check if they shared a Spotify song on their story
- If so, add it to a custom “IG Music” playlist
- Rerun once every 24 hours

Notes:
- Put login information into secrets.py file
"""

import json
import requests
from secrets import spotify_user_id, spotify_token
from selenium import webdriver

class CreateInstagramPlaylist:
	def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.driver = webdriver.Chrome()
        self.driver.get("https://instagram.com")

    def get_songs_from_ig(self):
        pass

    def create_playlist(self):
        request_body = json.dumps({
            "name": "Instagram Recommendations",
            "description": "Songs shared to Stories by people I follow",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        # playlist id
        return response_json['id']

    def get_spotify_uri(self, song_name, artist):
        pass
    
    def add_song_to_playlist(self):
        pass
