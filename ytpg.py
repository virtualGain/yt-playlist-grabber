import os
import json
import yt_dlp

# Set the user name and download directory
user_name = "USER_NAME"
download_dir = "/path/to/download/directory/"

# Load previously downloaded video list from file
prev_downloaded_file = os.path.join(download_dir, "prev_downloaded.json")
if os.path.exists(prev_downloaded_file):
    with open(prev_downloaded_file, "r") as f:
        prev_downloaded = json.load(f)
else:
    prev_downloaded = []

# Set yt-dlp options for MP3 conversion
ytdlp_opts = {
    "format": "bestaudio[ext=m4a]/bestaudio",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "320",
    }],
}

# Initialize yt-dlp downloader
ytdl = yt_dlp.YoutubeDL(ytdlp_opts)

# Get user's public playlists
user_playlists_url = f"https://www.youtube.com/user/{user_name}/playlists"
user_playlists_info = ytdl.extract_info(user_playlists_url, download=False)

# Download videos from each playlist
for playlist in user_playlists_info["entries"]:
    playlist_dir = os.path.join(download_dir, playlist["title"])
    os.makedirs(playlist_dir, exist_ok=True)
    
    # Load previously downloaded video list for this playlist
    playlist_downloaded_file = os.path.join(playlist_dir, "prev_downloaded.json")
    if os.path.exists(playlist_downloaded_file):
        with open(playlist_downloaded_file, "r") as f:
            playlist_downloaded = json.load(f)
    else:
        playlist_downloaded = []
    
    # Download videos from playlist
    playlist_info = ytdl.extract_info(playlist["url"], download=False)
    for video in playlist_info["entries"]:
        # Check if video has already been downloaded
        if video["id"] not in prev_downloaded and video["id"] not in playlist_downloaded:
            # Download video and convert to MP3
            ytdl.download([video["webpage_url"]], outtmpl=os.path.join(playlist_dir, "%(title)s.%(ext)s"))
            
            # Add video ID to previously downloaded list for both the playlist and overall downloaded lists
            prev_downloaded.append(video["id"])
            playlist_downloaded.append(video["id"])
            
    # Save updated previously downloaded video list for this playlist to file
    with open(playlist_downloaded_file, "w") as f:
        json.dump(playlist_downloaded, f)
    
# Save updated overall previously downloaded video list to file
with open(prev_downloaded_file, "w") as f:
    json.dump(prev_downloaded, f)
