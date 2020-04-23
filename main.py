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
- Scrape Spotify OAuth token from website
- Automate script to run once a day
"""

import json
import requests
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from secrets import spotify_user_id, spotify_password, instagram_user_id, instagram_password

class InstagramToSpotifyBot:
    def __init__(self):
        self.spotify_user_id = spotify_user_id
        self.spotify_password = spotify_password
        self.instagram_user_id = instagram_user_id
        self.instagram_password = instagram_password
        self.all_track_uris = []
        self.playlist_id = ''

        current_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        print('Current Time: ', current_time)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_options)

        # Scrape Spotify OAuth token
        self.driver.get("https://developer.spotify.com/console/post-playlists/?user_id=&body=%7B%22name%22%3A%22New%20Playlist%22%2C%22description%22%3A%22New%20playlist%20description%22%2C%22public%22%3Afalse%7D")
        self.driver.find_element_by_xpath("//button[contains(text(), 'Get Token')]").click()
        self._wait(EC.element_to_be_clickable((By.ID, "oauthRequestToken")))
        self.driver.find_element_by_id("oauthRequestToken").click()
        self._login_to_spotify(spotify_user_id, spotify_password)
        self.spotify_token = self.driver.find_element_by_id("oauth-input").get_attribute("value")

        # Login to Instagram
        self.driver.get("https://instagram.com")
        self._wait(EC.presence_of_element_located((By.NAME, "username")))
        self._login_to_instagram(instagram_user_id, instagram_password)

    # def setup(self):
    #     # open spotify
    #     # self.driver.get("https://open.spotify.com")
    #     # self._login_to_spotify(spotify_user_id, spotify_password)

    #     # open instagram
    #     # self.driver.execute_script('window.open("https://instagram.com","_blank");')
    #     self.driver.get("https://instagram.com")
    #     self._wait(EC.presence_of_element_located((By.NAME, "username")))

    #     # close spotify
    #     # self.driver.switch_to_window(self.driver.window_handles[0])
    #     # self.driver.close()
        
    #     # start 
    #     # self.driver.switch_to_window(self.driver.window_handles[0])
    #     self._wait(EC.presence_of_element_located((By.NAME, "username")))
    #     self._login_to_instagram(instagram_user_id, instagram_password)

    def get_songs_from_stories(self):
        # Start watching stories

        # self._wait(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Watch All')]")))
        # self.driver.find_element_by_xpath("//div[contains(text(), 'Watch All')]").click()
        # self._wait(EC.presence_of_element_located((By.CLASS_NAME, "c6Ldk"))).click()
        
        self.driver.implicitly_wait(5)
        # self.driver.find_element_by_class_name("c6Ldk").click()
        self.driver.find_element_by_xpath("//div[contains(text(), 'Watch All')]").click()
        
        # viewing_story = self._wait(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        viewing_story = self._wait(EC.url_contains('stories'))
        while viewing_story:
            # print('viewing story')
            # right = self._wait(EC.element_to_be_clickable((By.XPATH, "//div[@class='coreSpriteRightChevron']")))
            # right = self.driver.find_element_by_xpath("//div[@class='coreSpriteRightChevron']")

            # "Right" button
            # right = self.driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)

            try:
                # "Play on Spotify" link
                self.driver.find_element_by_xpath("//div[contains(text(), 'Play on Spotify')]").click()
        
                # "Open Spotify" pop-up
                self.driver.find_element_by_class_name("vbsLk").click()
                self._wait(EC.new_window_is_opened(self.driver.window_handles))

                # switch to spotify window
                self.driver.switch_to_window(self.driver.window_handles[1])
                self._wait(EC.url_contains('track:'))

                # Get track uri from the browser url (ex. https://open.spotify.com/album/600ClrWRsAr7jZ0qjaBLHz?highlight=spotify:track:2Aq78kKI9yuloJQkcbhQbU)
                url = self.driver.current_url
                track_tag = 'track:'
                track_uri = url[url.index(track_tag) + len(track_tag):]
                print("FEATURED TRACK URI: ", track_uri)
                self.all_track_uris.append(track_uri)
                self.driver.close()

                # switch back to instagram window
                self.driver.switch_to_window(self.driver.window_handles[0])

                # Press "right arrow" key
                self.driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)
                
                # self._wait(EC.presence_of_element_located((By.XPATH, "//div[@class='coreSpriteRightChevron']")))
                # self.driver.find_element_by_xpath("//div[@class='coreSpriteRightChevron']").click()
                self.driver.implicitly_wait(1)
            
            except Exception:
                # Press "right arrow" key
                self.driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)
                
                # self._wait(EC.presence_of_element_located((By.XPATH, "//div[@class='coreSpriteRightChevron']")))
                # self.driver.find_element_by_xpath("//div[@class='coreSpriteRightChevron']").click()
                # print('pressed right arrow key')
                self.driver.implicitly_wait(1)
        
        if len(self.all_track_uris) > 0:
            return self.all_track_uris
        else:
            print('No songs today!')
            self.driver.quit()

    def add_songs_to_playlist(self):
        # collect all track uri's
        uris = self.all_track_uris
        if len(uris) != 0:
        
            # navigate playlists
            get_query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
            get_response = requests.get(
                get_query,
                headers={
                    "Authorization": "Bearer {}".format(self.spotify_token)
                }
            )

            get_response_json = get_response.json()
            playlist_names = [playlist['name'] for playlist in get_response_json['items']]

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
                    "Authorization": "Bearer {}".format(self.spotify_token)
                }
            )

            self.driver.quit()
            return post_response.json()

        else:
            print("No songs recommended today :(")
            self.driver.quit()

    def _wait(self, expected_condition):
        return WebDriverWait(self.driver, 15).until(expected_condition)
    
    def _login_to_instagram(self, instagram_user_id, instagram_password):
        self.driver.find_element_by_name("username").send_keys(instagram_user_id)
        self.driver.find_element_by_name("password").send_keys(instagram_password)
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        self._wait(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]")))
        self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
    
    def _login_to_spotify(self, spotify_user_id, spotify_password):
        # self.driver.find_element_by_xpath("//button[contains(text(), 'Log in')]").click()
        self._wait(EC.presence_of_element_located((By.NAME, "username")))
        self.driver.find_element_by_name("username").send_keys(spotify_user_id)
        self.driver.find_element_by_name("password").send_keys(spotify_password)
        self.driver.find_element_by_id("login-button").click()
        self.driver.implicitly_wait(10)
        # self._wait(EC.staleness_of((By.ID, "login-button")))
    
    # def _authorize_spotify(self):
    #     query = "https://accounts.spotify.com/authorize"
    #     scope = "playlist-read-private playlist-read-collaborative"
    #     redirect_uri = "http://localhost:8888/callback"
    #     response = requests.get(
    #         query,
    #         params={
    #             "client_id": client_id,
    #             "response_type": "code",
    #             "redirect_uri": redirect_uri,
    #             "scope": scope
    #         }
    #     )
    #     authorization_code = response

    #     request_body = json.dumps({
    #         "grant_type": "authorization_code",
    #         "code": authorization_code,
    #         "redirect_uri": redirect_uri,
    #     })

    #     query = "https://accounts.spotify.com/api/token"
    #     response = requests.post(
    #         query,
    #         data=request_body,
    #         headers={
    #             "Authorization": "Basic {}".format(client_encoded)
    #         }
    #     )
    #     tokens = response.json()
    #     print(tokens['access_token'])
    
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
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()

        # playlist id
        self.playlist_id = response_json['id']

    # def func(self):
    #     get_query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
    #     get_response = requests.get(
    #         get_query,
    #         headers={
    #             "Authorization": "Bearer {}".format(spotify_token)
    #         }
    #     )

    #     print(get_response.json())

bot = InstagramToSpotifyBot()
bot.get_songs_from_stories()
bot.add_songs_to_playlist()