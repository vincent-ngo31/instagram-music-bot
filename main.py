"""
Tools
- Spotify Web API
- InstaBot API

Steps:
- Login to Instagram using my account
- Access the Stories of the users I follow
- Check if they shared a Spotify song on their story
- If so, add it to a custom “IG Music” playlist
- Rerun once every 24 hours

Notes:
- Use InstaBot to get list of users you're following
- Navigate to those users' stories and check for songs
"""

import json
import requests
from time import sleep
from secrets import spotify_user_id, spotify_token, instagram_user_id, instagram_password
from selenium import webdriver

class CreateInstagramPlaylist:
    def __init__(self):
        self.spotify_user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.instagram_user_id = instagram_user_id
        self.instagram_password = instagram_password
    
    def login_to_instagram(self, instagram_user_id, instagram_password):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://instagram.com")
        sleep(4)
        # self.driver.find_element_by_xpath("//a[contains(text(), 'Log in')]").click()
        # sleep(2)
        self.driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(instagram_user_id)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(instagram_password)
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        sleep(4)
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
        sleep(2)
    
    def get_songs_from_stories(self):
        # /section/header/div/div[1]/div/div[2]/div/div[1]
        # /div/div/div[1]
        # /div/div/div[1]
        pass
        
    def create_playlist(self):
        request_body = json.dumps({
            "name": "Instagram Recommendations",
            "description": "Songs shared to Stories by people I follow",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.spotify_user_id)
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

bot = CreateInstagramPlaylist()
bot.login_to_instagram(instagram_user_id, instagram_password)
