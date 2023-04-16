#example usage: python "C:\Users\mikey\git-repos\yt-playlist-grabber\ytpg.py" elysiandreamz --download-dir /path/to/custom/download/directory
#downloads videos from public playlist for given username and converts them to mp3 format adding id3 tags based on playlist and video naming standard

import os
import json
import argparse
import yt_dlp
import datetime
from music_tag import load_file

def add_tags(file_path, title, playlist_name):
    # Parse artist and title from video title
    if "-" in title:
        artist, title = [s.strip() for s in title.split("-", 1)]
    else:
        artist = ""
    # Parse genre from playlist name
    if "-" in playlist_name:
        genre, _ = [s.strip() for s in playlist_name.split("-", 1)]
    else:
        genre = ""
    # Set ID3 tags
    audio_file = load_file(file_path)
    audio_file['title'] = title
    audio_file['artist'] = artist
    audio_file['genre'] = genre
    audio_file['comment'] = f"This mp3 was downloaded from YouTube from the following playlist: {playlist_name}"
    # Save changes
    audio_file.save()

def download_playlists(user_name, download_dir):
    ytdlp_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
        }
    ytdl = yt_dlp.YoutubeDL(ytdlp_opts)

    # Get user's public playlists
    user_playlists_url = f"https://www.youtube.com/user/{user_name}/playlists"
    user_playlists_info = ytdl.extract_info(user_playlists_url, download=False)

    # Download videos from each playlist
    for playlist in user_playlists_info["entries"]:
        playlist_dir = os.path.join(download_dir, playlist["title"])
        os.makedirs(playlist_dir, exist_ok=True)

        # Set yt-dlp options for MP3 conversion
        ytdl.params["outtmpl"] = os.path.join(playlist_dir, "%(title)s.%(ext)s")

        # Initialize yt-dlp downloader
        ytdl = yt_dlp.YoutubeDL(ytdlp_opts)

        # Load previously downloaded video list for this playlist
        playlist_downloaded_file = os.path.join(playlist_dir, "prev_downloaded.json")
        if os.path.exists(playlist_downloaded_file):
            with open(playlist_downloaded_file, "r") as f:
                playlist_downloaded = json.load(f)
        else:
            playlist_downloaded = []

        # Download videos from playlist
        playlist_info = ytdl.extract_info(playlist["webpage_url"], download=False)
        for video in playlist_info["entries"]:
            # Check if video has already been downloaded
            if not any(playlist_downloaded_vids["video_id"] == video["id"] for playlist_downloaded_vids in playlist_downloaded):
                # Download video and convert to MP3
                ytdl.download([video["webpage_url"]])

                # Add ID3 tags to MP3 file
                mp3_file_path = os.path.join(playlist_dir, f"{video['title']}.mp3")
                add_tags(mp3_file_path, video['title'], playlist["title"])

                # Add video ID to previously downloaded list for both the playlist and overall downloaded lists
                playlist_downloaded.append({"video_title": video["title"],
                                            "video_id": video["id"],
                                            "dl_date": datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")})

        # Save updated previously downloaded video list for this playlist to file
        with open(playlist_downloaded_file, "w") as f:
            json.dump(playlist_downloaded, f)

if __name__ == "__main__":
    # Set default download directory
    default_download_dir = "c:/music/ytpg"
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Download all public playlists from a YouTube user")
    parser.add_argument("user_name", help="YouTube user name")
    parser.add_argument("--download-dir", dest="download_dir", default=default_download_dir, help="Directory to download videos to")
    args = parser.parse_args()

    # Download playlists
    download_playlists(args.user_name, args.download_dir)
