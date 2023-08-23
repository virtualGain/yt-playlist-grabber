#example usage: python "C:\Users\mikey\git-repos\yt-playlist-grabber\ytpg.py" elysiandreamz --download-dir /path/to/custom/download/directory
#downloads videos from public playlist for given username and converts them to mp3 format adding id3 tags based on playlist and video naming standard

import os
import json
import argparse
import yt_dlp
import datetime
import sys
import clr
import subprocess
from pathvalidate import sanitize_filename
from music_tag import load_file
from colorama import Fore, Style
global ERROR_LOGS_FILEPATH

""" USE IN THE FUTURE TO MAKE FASTER/BETTER
def get_playlists(user_name):
    API_KEY = 'your_youtube_data_api_key'
    YOUTUBE_API_BASE_URL = 'https://www.googleapis.com/youtube/v3'
    url = f"{YOUTUBE_API_BASE_URL}/channels?part=contentDetails&forUsername={user_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'items' not in data:
        raise ValueError('Invalid user name or API key')
    
    channel_id = data['items'][0]['id']
    
    url = f"{YOUTUBE_API_BASE_URL}/playlists?part=snippet&channelId={channel_id}&maxResults=50&key={api_key}"
    response = requests.get(url)
    data = response.json()

    playlist_urls = [f"https://www.youtube.com/playlist?list={item['id']}" for item in data['items']]
    return playlist_urls
"""

def log_error_to_file(error_message):
    #get time and add to message
    now = datetime.datetime.now()
    error_message = now.strftime('%Y-%m-%d %H:%M:%S') + ": " + error_message

    with open(ERROR_LOGS_FILEPATH, "a") as log_file:
        log_file.write(f"{error_message}\n")

def download_videos_from_pl(playlist, playlist_dir):
    # Load previously downloaded videos list for this playlist
    playlist_downloaded_file = os.path.join(playlist_dir, "prev_downloaded.json")
    if os.path.exists(playlist_downloaded_file):
        with open(playlist_downloaded_file, "r") as f:
            playlist_downloaded = json.load(f)
    else:
        playlist_downloaded = []

    #playlist_info = ytdl.extract_info(playlist["webpage_url"], download=False)
    for video in playlist["entries"]:
        if video is not None: 
            # Check if video has already been downloaded
            if not any(playlist_downloaded_vids["video_id"] == video["id"] for playlist_downloaded_vids in playlist_downloaded):
                
                # Santize the filepath
                safe_vid_title = sanitize_filename(video['title'])
                mp3_file_path = os.path.join(playlist_dir, safe_vid_title).replace("\\","/")

                #reinit ytdl with updated path. Only way to sanitize filenames
                ytdlp_opts = {
                    "format": "bestaudio[ext=m4a]/bestaudio",
                    "sleep_interval": 2,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }],
                    "outtmpl": mp3_file_path + ".%(ext)s",
                    "ignorerrors": True,
                    "quiet": True,
                }
                ytdl = yt_dlp.YoutubeDL(ytdlp_opts)
                # Download video and convert to MP3 
                print(Fore.YELLOW + f"Processing Video title: {video['title']}" + Style.RESET_ALL)
                print(Fore.YELLOW + f"Video URL: {video['webpage_url']}" + Style.RESET_ALL)
                try: 
                    ytdl.download([video['webpage_url']])
                    # Add ID3 tags to MP3
                    add_tags(mp3_file_path + ".mp3", safe_vid_title, playlist["title"])
                    # Add video ID to previously downloaded list for both the playlist and overall downloaded lists
                    playlist_downloaded.append({"video_title": safe_vid_title,
                                                "video_id": video["id"],
                                                "dl_date": datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")})
                    
                    # Save updated previously downloaded video list for this playlist to file
                    with open(playlist_downloaded_file, "w") as f:
                        json.dump(playlist_downloaded, f)
                except: 
                    print(Fore.RED + f"Failed processing video: {video['title']}" + Style.RESET_ALL)
                
        else: 
            error_message = f"ERROR: Encountered None type video in playlist: {playlist['title']}"
            print(Fore.RED + error_message + Style.RESET_ALL)
            log_error_to_file(error_message=error_message)

def add_crate_to_serato(playlist_name, directory_path):
    # Add the Serato SDK assembly to the .NET CLR
    serato_sdk_path = "C:\\Program Files\\Serato\\Serato DJ Pro\\SeratoSDK.dll"
    clr.AddReferenceToFileAndPath(serato_sdk_path)

    # Import the necessary Serato SDK classes
    from SeratoSDK import Engine, Crate, Track
    # Create a new Serato Engine object
    engine = Engine()

    # Initialize the Serato Engine
    if not engine.InitializeEngine():
        print("Failed to initialize the Serato Engine.")
        sys.exit(1)

    # Create a new crate with the specified name
    crate_name = playlist_name
    crate = Crate(crate_name)

    # Get the list of music files in the specified directory
    music_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f)) and f.lower().endswith((".mp3", ".wav", ".aiff", ".flac"))]

    # Add each music file to the crate as a new track
    for music_file in music_files:
        track = Track(music_file)
        if not crate.Tracks_Add(track):
            print(f"Failed to add track '{music_file}' to crate '{crate_name}'.")

    # Add the crate to the Serato Engine
    if not engine.Crates_Add(crate):
        print(f"Failed to add crate '{crate_name}' to the Serato Engine.")
        sys.exit(1)

    # Release the Serato Engine
    engine.ShutdownEngine()

    print(f"Successfully added crate '{crate_name}' to Serato with {len(music_files)} tracks.")

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
    audio_file = load_file(file_path.replace('"', ''))
    audio_file['title'] = title
    audio_file['artist'] = artist
    audio_file['genre'] = genre
    audio_file['comment'] = f"downloaded from playlist: {playlist_name}."
    # Save changes
    audio_file.save()

def download_playlists(user_name, download_dir, playlist_title):
    ytdlp_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
            "outtmpl": "%(title)s.%(ext)s".replace("\\", "/"),
            "ignoreerrors": True,
        }
    ytdl = yt_dlp.YoutubeDL(ytdlp_opts)

    # Get user's public playlists
    user_playlists_url = f"https://www.youtube.com/user/{user_name}/playlists"
    print(Fore.YELLOW + "Extracting Playlist Data Now this may take a few minutes" + Style.RESET_ALL)
    user_playlists_info = ytdl.extract_info(user_playlists_url, download=False)

    # Download videos from each playlist
    for playlist in user_playlists_info["entries"]:
        if playlist is not None:
            print(Fore.YELLOW + f"Processing Playlist title: {playlist['title']}" + Style.RESET_ALL)
            playlist_dir = os.path.join(download_dir, playlist["title"])
            os.makedirs(playlist_dir, exist_ok=True)

            # Download videos from playlist
            download_videos_from_pl(playlist, playlist_dir)

            #add crate to serato DJ pro
            #add_crate_to_serato("ytpg_" + playlist["title"], playlist_dir )
        else: 
            error_message = f"ERROR: Encountered None type playlist"
            print(Fore.RED + error_message + Style.RESET_ALL)
            log_error_to_file(error_message=error_message)

def run_itunes_powershell_script(script_path, directory_path):
    try:
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-File", script_path, "-directoryPath", directory_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: Unable to update playlists")

def run_backup_powershell_script(script_path, SourceFolderPath, DestinationFolderName):
    try:
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-File", script_path, "-SourceFolderPath", SourceFolderPath, "-DestinationFoldername", DestinationFolderName],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        error_message = f"Error: Unable to update playlists" + e.stdout
        log_error_to_file(error_message=error_message)
        print(error_message)

if __name__ == "__main__":
    import time
    start_time = time.time()

    # Set default download directory
    default_download_dir = "c:\\music\\ytpg"
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Download all public playlists from a YouTube user")
    parser.add_argument("user_name", help="YouTube user name")
    parser.add_argument("--download-dir", dest="download_dir", default=default_download_dir, help="Directory to download videos to")
    args = parser.parse_args()
    ERROR_LOGS_FILEPATH = args.download_dir + "ERROR_LOG"

    # Download playlists
    download_playlists(args.user_name, args.download_dir)

    # update itunes playlists
    powershell_script_path = "./update_itunes_playlists.ps1"
    run_itunes_powershell_script(powershell_script_path, args.download_dir)
    
    # spit out the script runtime in minutes
    end_time = time.time()
    total_runtime = end_time - start_time
    total_runtime_minutes = total_runtime / 60
    print("Total runtime: {:.2f} minutes".format(total_runtime_minutes))

    #backup our music folder
    start_time = time.time()
    run_backup_powershell_script("./backup_to_onedrive.ps1", "C:\Music", "Music_Backup")

    end_time = time.time()
    total_runtime = end_time - start_time
    total_runtime_minutes = total_runtime / 60
    print("Total runtime: {:.2f} minutes".format(total_runtime_minutes))
