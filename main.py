"""
Tools
- Selenium
- Spotify Web API


Steps:
- Login to Instagram and Spotify with my accounts
- Access the Stories of the users I follow
- Check if they shared a Spotify song on their story
- If so, add it to a custom “IG Music” playlist
- Rerun once every 24 hours

Notes:
- How to parse song name and artist name?
"""

import json
import requests
from time import sleep
from secrets import spotify_user_id, spotify_password, spotify_token, instagram_user_id, instagram_password
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class CreateInstagramPlaylist:
    def __init__(self):
        self.spotify_user_id = spotify_user_id
        self.spotify_password = spotify_password
        self.spotify_token = spotify_token
        self.instagram_user_id = instagram_user_id
        self.instagram_password = instagram_password

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # self.driver = webdriver.Chrome(options=chrome_options)

        self.driver = webdriver.Chrome()
        self.driver.get("https://open.spotify.com")
        sleep(3)
        # New tab (not working)
        self.driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
        self.driver.get("https://instagram.com")
        sleep(3)
    
    def login_to_instagram(self, instagram_user_id, instagram_password):
        self.driver.find_element_by_name("username").send_keys(instagram_user_id)
        self.driver.find_element_by_name("password").send_keys(instagram_password)
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        sleep(3)
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
        sleep(3)
    
    def login_to_spotify(self, spotify_user_id, spotify_password):
        pass
    
    def get_songs_from_stories(self):
        # Start watching stories
        self.driver.find_element_by_xpath("//div[contains(text(), 'Watch All')]").click()
        sleep(2)
        
        story = self.driver.find_element_by_xpath("//div[@role='dialog']")
        while story:
            # Check for Spotify song
            # play_song = self.driver.find_element_by_xpath("//div[contains(text(), 'Play on Spotify')]")

            # "Right" button
            right = self.driver.find_element_by_xpath("//div[@class='coreSpriteRightChevron']")
            try:
                # "Play on Spotify" link
                self.driver.find_element_by_xpath("//div[contains(text(), 'Play on Spotify')]").click()
                # "Open Spotify" pop-up
                self.driver.find_element_by_class_name("vbsLk").click()
                sleep(3)
            except Exception:
                right.click()
                sleep(1)

            # Click "Next" button
            # self.driver.find_element_by_xpath("//div[@class='coreSpriteRightChevron']").click()
            
    def create_playlist(self):
        request_body = json.dumps({
            "name": "Instagram Recommendations",
            "description": "Songs shared to Stories by people I follow",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
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
        "Search for song"
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        # only use the first song
        uri = songs[0]["uri"]

        return uri
    
    def add_song_to_playlist(self, song_name, artist):
        pass

bot = CreateInstagramPlaylist()
# bot.login_to_instagram(instagram_user_id, instagram_password)
# bot.get_songs_from_stories()
