import json
import requests

from time import sleep
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

from secrets import spotify_user_id, spotify_password, instagram_user_id, instagram_password

class InstagramMusicBot:
    def __init__(self):
        self.current_time = datetime.now().strftime("%d-%b-%Y")
        self.spotify_user_id = spotify_user_id
        self.spotify_password = spotify_password
        self.instagram_user_id = instagram_user_id
        self.instagram_password = instagram_password
        self.all_track_uris = []
        self.playlist_id = ''

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_options)

        # Get OAuth token and log in to Spotify
        self.driver.get("https://developer.spotify.com/console/post-playlists/?user_id=&body=%7B%22name%22%3A%22New%20Playlist%22%2C%22description%22%3A%22New%20playlist%20description%22%2C%22public%22%3Afalse%7D")
        self.driver.find_element_by_xpath("//button[contains(text(), 'Get Token')]").click()
        self.wait(EC.element_to_be_clickable((By.ID, "oauthRequestToken")))
        self.driver.find_element_by_id("oauthRequestToken").click()
        self.login_to_spotify(spotify_user_id, spotify_password)
        self.spotify_token = self.driver.find_element_by_id("oauth-input").get_attribute("value")

        # Login to Instagram
        self.driver.get("https://instagram.com")
        self.wait(EC.presence_of_element_located((By.NAME, "username")))
        self.login_to_instagram(instagram_user_id, instagram_password)

    def get_songs_from_stories(self):
        # Start watching stories
        self.wait(EC.element_to_be_clickable((By.XPATH, "//div[@class='RR-M-  QN629']"))).click()
        print('Viewing stories...')

        while self.wait(EC.url_contains('stories')):

            
            try:
                
                # "Play on Spotify" link
                self.retrying_spotify_click()
                
                # Get sharer's username
                user_sharer = self.driver.find_element_by_xpath("//a[@class='FPmhX notranslate  R4sSg']").get_attribute("title")

                # "Open Spotify" pop-up
                self.driver.find_element_by_class_name("vbsLk").click()
                self.driver.switch_to_window(self.driver.window_handles[1])
                self.wait(EC.url_contains('track:'))

                url = self.driver.current_url

                # Add track uri and link song
                if 'track' in url:
                    track_tag = 'highlight='
                    track_uri = url[url.index(track_tag) + len(track_tag):]
                    self.all_track_uris.append(track_uri)
                    print("Song shared by {}: {}".format(user_sharer, url))
                # Anything other than songs will only be linked
                elif 'album' in url:
                    print("Album shared by {}: {}".format(user_sharer, url))
                elif 'artist' in url:
                    print("Artist shared by {}: {}".format(user_sharer, url))
                elif 'playlist' in url:
                    print("Playlist shared by {}: {}".format(user_sharer, url))
                elif 'episode' in url:
                    print("Podcast shared by {}: {}".format(user_sharer, url))
                elif 'show' in url:
                    print("Podcast shared by {}: {}".format(user_sharer, url))
                self.driver.close()

                # Switch back to instagram window
                self.driver.switch_to_window(self.driver.window_handles[0])

                # Input "right arrow" key
                self.driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)
                self.driver.implicitly_wait(1)
            
            except NoSuchElementException:

                # Press "right arrow" key
                self.driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)
                self.driver.implicitly_wait(1)

    def add_songs_to_playlist(self):
        # collect all track uri's
        uris = self.all_track_uris
        if len(uris) != 0:
            
            # Make new playlist
            print('Creating new playlist...')
            self.create_playlist()

            # Add songs to playlist
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
            print("Songs have been added to your new playlist!")
            self.driver.quit()
            return post_response.json()

        else:
            print("No songs were shared today!")
            self.driver.quit()

    def wait(self, expected_condition):
        try:
            return WebDriverWait(self.driver, 5).until(expected_condition)
        except TimeoutException:
            pass
    
    def login_to_instagram(self, instagram_user_id, instagram_password):
        self.driver.find_element_by_name("username").send_keys(instagram_user_id)
        self.driver.find_element_by_name("password").send_keys(instagram_password)
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        # First guaranteed pop-up
        self.wait(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))).click()
        # Second occasional pop-up
        if self.wait(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))):
            self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()

    def login_to_spotify(self, spotify_user_id, spotify_password):
        self.wait(EC.presence_of_element_located((By.NAME, "username")))
        self.driver.find_element_by_name("username").send_keys(spotify_user_id)
        self.driver.find_element_by_name("password").send_keys(spotify_password)
        self.driver.find_element_by_id("login-button").click()
        self.driver.implicitly_wait(10)
    
    def retrying_spotify_click(self):
        attempts = 0
        while(attempts < 2):
            try:
                self.driver.find_element_by_xpath("//div[contains(text(), 'Play on Spotify')]").click()
                return
            except StaleElementReferenceException:
                pass
            attempts += 1
        return StaleElementReferenceException

    def create_playlist(self):
        playlist_name = "Instagram Music ({})".format(self.current_time)
        request_body = json.dumps({
            "name": playlist_name,
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
        self.playlist_id = response_json['id']

if __name__ == '__main__':
    bot = InstagramMusicBot()
    bot.get_songs_from_stories()
    bot.add_songs_to_playlist()