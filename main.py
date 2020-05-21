import sys
import argparse
import json
import requests
import schedule
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

class InstagramMusicBot:
    def __init__(self, driver, spotify_user_id, spotify_password, instagram_user_id, instagram_password):
        self.current_time = datetime.now().strftime("%d-%b-%Y %H:%M")
        self.spotify_user_id = spotify_user_id
        self.spotify_password = spotify_password
        self.instagram_user_id = instagram_user_id
        self.instagram_password = instagram_password
        self.all_track_uris = []
        self.playlist_id = ''
        self.driver = driver

        # Current session
        print("Session date: {}".format(self.current_time))

        # Get OAuth token and log in to Spotify
        print('Scraping token...')
        SPOTIFY_URL = "https://developer.spotify.com/console/post-playlists/?user_id=&body=%7B%22name%22%3A%22New%20Playlist%22%2C%22description%22%3A%22New%20playlist%20description%22%2C%22public%22%3Afalse%7D"
        driver.get(SPOTIFY_URL)
        driver.find_element_by_xpath("//button[contains(text(), 'Get Token')]").click()
        self.wait(EC.element_to_be_clickable((By.ID, "oauthRequestToken")))
        driver.find_element_by_id("oauthRequestToken").click()
        print("Logging into Spotify...")
        self.login_to_spotify(spotify_user_id, spotify_password)
        self.spotify_token = driver.find_element_by_id("oauth-input").get_attribute("value")

        # Login to Instagram
        print("Logging into Instagram...")
        driver.get("https://instagram.com")
        self.wait(EC.presence_of_element_located((By.NAME, "username")))
        self.login_to_instagram(instagram_user_id, instagram_password)

    def get_songs_from_stories(self):
        # Start watching stories
        self.wait(EC.element_to_be_clickable((By.XPATH, "//div[@class='RR-M-  QN629']")))
        driver.find_element_by_xpath("//div[@class='RR-M-  QN629']").click()
        
        # Check for "Live" accounts and bypass
        self.check_live()
        
        print('Viewing stories...')
        while self.wait(EC.url_contains('stories')):
            
            try:
                
                # "Play on Spotify" link
                self.retrying_spotify_click()
                
                # Get sharer's username
                user_sharer = driver.find_element_by_xpath("//a[@class='FPmhX notranslate  R4sSg']").get_attribute("title")

                # "Open Spotify" pop-up
                driver.find_element_by_class_name("vbsLk").click()
                driver.switch_to_window(driver.window_handles[1])
                self.wait(EC.url_contains('track'))

                url = driver.current_url

                # Add track uri and link song
                if 'track' in url:
                    track_tag = 'track/'
                    end_tag = '?'
                    prefix = 'spotify:track:'
                    # track_uri = url[url.index(track_tag) + len(track_tag):]
                    track_uri = prefix + url[url.index(track_tag) + len(track_tag) : url.index(end_tag)]
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
                driver.close()

                # Switch back to instagram window
                driver.switch_to_window(driver.window_handles[0])

                # Input "right arrow" key
                driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)
                driver.implicitly_wait(1)
            
            except NoSuchElementException:

                # Press "right arrow" key
                driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)
                driver.implicitly_wait(1)

    def add_songs_to_playlist(self, spotify_user_id):
        # collect all track uri's
        uris = self.all_track_uris
        if len(uris) != 0:
            
            # Make new playlist
            print('Creating new playlist...')
            self.create_playlist(spotify_user_id)

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
            driver.quit()
            return post_response.json()

        else:
            print("No songs were shared today!")
            driver.quit()

    def wait(self, expected_condition):
        try:
            return WebDriverWait(driver, 5).until(expected_condition)
        except TimeoutException:
            pass
    
    def login_to_instagram(self, instagram_user_id, instagram_password):
        driver.find_element_by_name("username").send_keys(instagram_user_id)
        driver.find_element_by_name("password").send_keys(instagram_password)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        if self.wait(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))):
            driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()

    def login_to_spotify(self, spotify_user_id, spotify_password):
        self.wait(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element_by_name("username").send_keys(spotify_user_id)
        driver.find_element_by_name("password").send_keys(spotify_password)
        driver.find_element_by_id("login-button").click()
        driver.implicitly_wait(10)
    
    def retrying_spotify_click(self):
        attempts = 0
        while(attempts < 2):
            try:
                driver.find_element_by_xpath("//div[contains(text(), 'Play on Spotify')]").click()
                return
            except StaleElementReferenceException:
                pass
            attempts += 1
        return StaleElementReferenceException

    def check_live(self):
        url = driver.current_url
        while 'live' in url:
            driver.find_element_by_xpath("//svg[@aria-label='Close']").click()
            self.wait(EC.element_to_be_clickable((By.XPATH, "//canvas[@class='CfWVH']"))).click()
            # driver.find_element_by_xpath("//canvas[@class='CfWVH']")
    
    def create_playlist(self, spotify_user_id):
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

def run(driver, spotify_user_id, spotify_password, instagram_user_id, instagram_password):
    bot = InstagramMusicBot(driver, str(spotify_user_id), str(spotify_password), str(instagram_user_id), str(instagram_password))
    bot.get_songs_from_stories()
    bot.add_songs_to_playlist(spotify_user_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--spotify-user", required=True)
    parser.add_argument("--spotify-password", required=True)
    parser.add_argument("--ig-user", required=True)
    parser.add_argument("--ig-password", required=True)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--schedule", type=int, default=None)
    args = parser.parse_args()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    if args.headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument('start-maximized')
    driver = webdriver.Chrome(options=chrome_options)
    
    if args.schedule is not None:
        schedule.every().day.at(args.schedule).do(
            run, driver=driver, spotify_user_id=args.spotify_user, spotify_password=args.spotify_password, instagram_user_id=args.ig_user, instagram_password=args.ig_password
        )
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run(driver=driver, spotify_user_id=args.spotify_user, spotify_password=args.spotify_password, instagram_user_id=args.ig_user, instagram_password=args.ig_password)
