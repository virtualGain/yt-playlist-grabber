# yt-playlist-grabber

## YouTube Playlist Downloader
This is a Python script that uses yt-dlp to download videos from all public playlists belonging to a specific YouTube user. The script checks which videos have already been downloaded and only downloads videos that have not yet been downloaded.

The script also converts the downloaded videos to the highest quality MP3 format possible.

For each playlist, the script creates a subfolder in the download location to which the downloads will be saved. The script saves a separate prev_downloaded.json file in each playlist's subfolder to track which videos have been downloaded from that playlist, and also saves an overall prev_downloaded.json file in the download directory to track which videos have been downloaded overall.

In addition it also adds id3 tags that are parsed from the video name and playlist name. ID3 tags are added in the following way
artist: text before the "-"
title: text after the "-"
genre: text before the "-" in the playlist name
comment: "This video was downloaded from YouTube from the following playlist: YOURPLAYLISTHERE

## Dependencies
The script depends on the yt-dlp package, which can be installed using pip:

### Copy code
pip install yt-dlp

## Usage
To use this script as a CLI command, save the code as a file (e.g. ytpg.py) and run the following command in your terminal:

    python ytpg.py MyYouTubeUser --download-dir /path/to/custom/download/directory


This command will download playlists from the user "MyYouTubeUser" to the default download directory c:/music/ytpg.

If you want to specify a custom download directory, you can use the --download-dir argument just place /path/to/custom/download/directory with the path to the directory where you want to download the playlists. 

The script will download any new videos from each playlist.
The script will create a subfolder in download_dir for each of the user's public playlists, and will download videos from each playlist to its corresponding subfolder.

The script will also save a separate prev_downloaded.json file in each playlist's subfolder to track which videos have been downloaded from that playlist, and will update the overall prev_downloaded.json file in the download directory to track which videos have been downloaded overall.

The script will download any new videos from each playlist to its corresponding subfolder in the download directory.

# License
This script is licensed under the MIT License.
