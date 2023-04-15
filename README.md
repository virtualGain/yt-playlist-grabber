# yt-playlist-grabber

##YouTube Playlist Downloader
This is a Python script that uses yt-dlp to download videos from all public playlists belonging to a specific YouTube user. The script checks which videos have already been downloaded and only downloads videos that have not yet been downloaded.

The script also converts the downloaded videos to the highest quality MP3 format possible.

For each playlist, the script creates a subfolder in the download location to which the downloads will be saved. The script saves a separate prev_downloaded.json file in each playlist's subfolder to track which videos have been downloaded from that playlist, and also saves an overall prev_downloaded.json file in the download directory to track which videos have been downloaded overall.

##Dependencies
The script depends on the yt-dlp package, which can be installed using pip:

###Copy code
pip install yt-dlp

##Usage
Open the script file youtube_playlist_downloader.py in a text editor.
Set the user_name and download_dir variables at the top of the file to the desired values.
Save the file and exit the text editor.
Open a terminal and navigate to the directory containing the script file.
Run the script using the command python youtube_playlist_downloader.py.
The script will download any new videos from each playlist to its corresponding subfolder in the download directory.

#License
This script is licensed under the MIT License.
