# Instagram Music Bot
A bot that will find music shared in Instagram Stories by users you follow, provide links to these songs, and add them to a custom Spotify playlist. Shared albums, playlists, artists, podcasts, and podcast episodes will have only links provided.

### Built With:
* [Selenium Webdriver]
* [Spotify Web API]
* [Requests Library v 2.23.0]

### Local Setup
1) Install dependencies
`pip3 install -r requirements.txt`

2) Put your Spotify and Instagram login infomation into the secrets.py file
    * To find your Spotify User ID, log into Spotify, go into Account Overview, and look at your **Username**

3) Run script
`python3 main.py`

  [Selenium Webdriver]: <https://www.selenium.dev/documentation/en/webdriver/>
  [Spotify Web API]: <https://developer.spotify.com/documentation/web-api/>
  [Requests Library v 2.23.0]: <https://requests.readthedocs.io/en/master/>

### What it does
* Scrapes Spotify OAuth token
* Logs into Instagram and Spotify with your accounts
* Views the Stories of the users you follow
* Checks if someone shared a Spotify track, album, playlist, artist, podcast, or podcast episode on their story
* If so, displays a Spotify web player link to those media
* Once the bot is finished viewing stories, it generates a new custom “Instagram Music” playlist and adds all shared tracks to it

### To Do
* Tests
* More error handling
* Bypass users who are currently "Live" on Instagram

### Notes
* This bot mimics the user, so after you run the script, an automated browser window will pop up and execute all commands. You can let it run in the background, and once it's finished, expect a brand new playlist in your Spotify!

