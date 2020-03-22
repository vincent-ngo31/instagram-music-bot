"""
Tools
- Selenium
- Spotify Web API

Steps:
- Login to Instagram and Spotify with your accounts
- Access the Stories of the users you follow
- Check if they shared a Spotify song on their story
- If so, add it to a custom “IG Music” playlist
- Rerun once every 24 hours

Notes:
- replace sleep with wait
- automate token
- automate script to run once a day
"""

import json
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from secrets import spotify_user_id, spotify_password, spotify_token, instagram_user_id, instagram_password

class InstagramToSpotifyBot:
    def __init__(self):
        self.spotify_user_id = spotify_user_id
        self.spotify_password = spotify_password
        self.spotify_token = spotify_token
        self.instagram_user_id = instagram_user_id
        self.instagram_password = instagram_password
        self.all_track_uris = []
        self.playlist_id = ''

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_options)

    def setup(self):
        # open spotify
        self.driver.get("https://open.spotify.com")
        self._login_to_spotify(spotify_user_id, spotify_password)
        
        # open instagram
        self.driver.execute_script('window.open("https://instagram.com","_blank");')
        sleep(3)
        
        # close spotify
        self.driver.switch_to_window(self.driver.window_handles[0])
        self.driver.close()
        
        # start 
        self.driver.switch_to_window(self.driver.window_handles[0])
        self._login_to_instagram(instagram_user_id, instagram_password)

    def get_songs_from_stories(self):
        # Start watching stories
        self.driver.find_element_by_xpath("//div[contains(text(), 'Watch All')]").click()
        sleep(2)
        
        story = self.driver.find_element_by_xpath("//div[@role='dialog']")
        while story:

            # "Right" button
            right = self.driver.find_element_by_xpath("//div[@class='coreSpriteRightChevron']")
            try:
                # "Play on Spotify" link
                self.driver.find_element_by_xpath("//div[contains(text(), 'Play on Spotify')]").click()
                
                # "Open Spotify" pop-up
                self.driver.find_element_by_class_name("vbsLk").click()
                sleep(3)
                
                # switch to spotify window
                self.driver.switch_to_window(self.driver.window_handles[1])
                
                # Get track uri from the browser url (ex. https://open.spotify.com/album/600ClrWRsAr7jZ0qjaBLHz?highlight=spotify:track:2Aq78kKI9yuloJQkcbhQbU)
                url = self.driver.current_url
                track_tag = 'track:'
                track_uri = url[url.index(track_tag) + len(track_tag):]
                print(track_uri)
                self.all_track_uris.append(track_uri)
                self.driver.close()
                
                # switch back to instagram window
                self.driver.switch_to_window(self.driver.window_handles[0])
                right.click()
                sleep(1)

            except Exception:
                right.click()
                sleep(1)
        
        return self.all_track_uris
    
    def add_songs_to_playlist(self):
        # collect all track uri's
        uris = self.all_track_uris

        # navigate playlists
        get_query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        get_response = requests.get(
            get_query,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        get_response_json = get_response.json()
        playlist_names = get_response_json['items']['name']

        # if user does not have a playlist that matches this self.playlist_id
        if "Instagram Recommendations" not in playlist_names:
            self._create_playlist()
        
        # add songs to playlist
        request_data = json.dumps(uris)
        post_query = "https://api.spotify.com/v1/playlists/{}/tracks".format(self.playlist_id)
        post_response = requests.post(
            post_query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        return post_response.json()

    def _login_to_instagram(self, instagram_user_id, instagram_password):
        self.driver.find_element_by_name("username").send_keys(instagram_user_id)
        self.driver.find_element_by_name("password").send_keys(instagram_password)
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        sleep(3)
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
        sleep(3)
    
    def _login_to_spotify(self, spotify_user_id, spotify_password):
        self.driver.find_element_by_xpath("//button[contains(text(), 'Log in')]").click()
        sleep(3)
        self.driver.find_element_by_name("username").send_keys(spotify_user_id)
        self.driver.find_element_by_name("password").send_keys(spotify_password)
        self.driver.find_element_by_id("login-button").click()
        sleep(3)
    
    def _create_playlist(self):
        request_body = json.dumps({
            "name": "Instagram Recommendations",
            "description": "Scraped from my Stories feed using Instagram bot (@vincentdngo)",
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
        self.playlist_id = response_json['id']

bot = InstagramToSpotifyBot()
bot.setup()
bot.get_songs_from_stories()
bot.add_songs_to_playlist()