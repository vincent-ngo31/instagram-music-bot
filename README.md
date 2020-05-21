# Instagram Music Bot
A bot that will find music shared in Instagram Stories by users you follow, provide links to these songs, and add them to a custom Spotify playlist. After initializing the script, just let it run in the background. Once it's finished, expect a brand new playlist in your Spotify account! Works with Google Chrome.

### Built With:
* [Selenium Webdriver]
* [Spotify Web API]
* [Requests Library v 2.23.0]

### Local Setup
1) Install dependencies
`pip install -r requirements.txt`

2) Put your Spotify and Instagram login information into the **secrets.py** file
    * To find your Spotify User ID, search for your own profile on Spotify web player, and it should be in the url
    ![alt text](images/spotify_userid.png)

3) Run script
`python main.py`

  [Selenium Webdriver]: <https://www.selenium.dev/documentation/en/webdriver/>
  [Spotify Web API]: <https://developer.spotify.com/documentation/web-api/>
  [Requests Library v 2.23.0]: <https://requests.readthedocs.io/en/master/>

### What it does
* Scrapes Spotify OAuth token
   ![alt text](images/spotify_token_example.png)
* Logs into Instagram and Spotify with your accounts
* Views the Stories of the users you follow (1 sec. per Stories post)
* Checks if someone shared a Spotify track, album, playlist, artist, podcast, or podcast episode on their story
   ![alt text](images/shared_music.png)
* If so, displays Spotify web player links to those media and the users who shared them
   ![alt text](images/bot_output.png)
* Once the bot is finished viewing stories, it generates a new custom “Instagram Music” playlist and adds all shared tracks 
   ![alt text](images/new_playlist.png)

### To Do
* Tests
* More error handling
* Include option to automatically run once a day
