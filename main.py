import yt_dlp
import ffmpeg
import os
import json
import requests
import urllib.parse
import shutil
from pathlib import Path
from mutagen.easyid3 import EasyID3

os.environ["PATH"] += os.pathsep + r"D://instalki//ffmpeg-8.1.2-essentials_build//ffmpeg-8.1.2-essentials_build//bin"


def download(link):
    ydl_options = {
    "format": "bestaudio", # best or worst for video 
    "outtmpl": save_path+ "/%(title)s.%(ext)s"
    }

    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.download([link])

def search_mode():
    global artist_name, album_name, album_id, album_tracks
    if search_album == "y": 
        artist_name = input("provide artist name to search: ")
        album_name = input("provide album name: ")
        
        base_url = "https://itunes.apple.com/search"
        params = {"term": f"{artist_name} {album_name}", "media": "music", "entity": "album", "limit": 1}
        
        response = requests.get(base_url, params=params).json()
        results = response.get("results", [])
        
        if results and len(results) > 0:
            album_data = results[0]  
            album_id = album_data.get("collectionId")
            print(f"Found Album: {artist_name} - ID: {album_id}")
            

            lookup_url = "https://itunes.apple.com/lookup"
            lookup_params = {"id": album_id, "entity": "song"}
            lookup_data = requests.get(lookup_url, params=lookup_params).json()
        
            album_tracks = [item for item in lookup_data.get("results", []) if item.get("wrapperType") == "track"]
        else:
            print("Album not found on iTunes. Falling back to single lookup mode.")
            album_tracks = []

def find(start, name): #name can be *.webm for specific file type
    find = []
    for dir in Path(start).rglob(name):
        find.append(str(dir))
    return find

def convert(file_path): #from .webm to mp3
     for file in file_path:
        
        output_mp3 = os.path.splitext(file)[0] + ".mp3"
        mp3_files_path.append(output_mp3)
        # Słownik z flagami zawierającymi znaki specjalne (: oraz -)
        extra_args = {
            'c:a': 'libmp3lame',  # Wymusza kodek mp3
            'q:a': '2'            # Wysoka jakość dźwięku VBR (~190 kbps)
        }
        #-vn (wyłączenie wideo)
        stream = ffmpeg.input(file)
        stream = ffmpeg.output(stream, output_mp3, vn=None, **extra_args)
        ffmpeg.run(stream, overwrite_output=True)
        

def build_clear_dict(file_path):
    for file in file_path:
        song_title = str(os.path.basename(file))
        song_title = os.path.splitext(song_title)[0]
        songs.update({song_title : {"path":Path(file)}})



def request_data(url):
    o = requests.get(url)
    data = o.json()
    return data

def create_url(song_dict):
    for title, info in song_dict.items():
        base_url = "https://itunes.apple.com/search?"
        if search_album == "y" and artist_name and album_name:
            params = {"term": f"{title} {artist_name} {album_name}", "media": "music", "entity": "song", "limit": 1}
        else: 
            params = {"term": title, "media": "music", "entity": "song", "limit": 1}
        
        info["url"] = base_url + urllib.parse.urlencode(params)

# def search_singly(title:str):
#     paremeters = {"term": title , "media": "music", "entity": "song", "limit": 1}
#     return urllib.parse.urlencode(paremeters)

def search(song_dict):
    for title, info in song_dict.items():
        print(f"\nMatching: {title}")
        print("-" * 30)
        
        matched_track = None

        if search_album == "y" and album_tracks:
            for track in album_tracks:
                track_name = track.get("trackName", "").lower()
                if track_name in title.lower() or title.lower() in track_name:
                    matched_track = track
                    break
        if not matched_track:
            o = request_data(info["url"])
            if o.get("results"):
                matched_track = o["results"][0]
        if not matched_track: 
            print("something went horribly wrong, please fill data manualy ")
            info["title"] = confirm_field("title","")
            info["artist"] = confirm_field("artist","")
            info["album"] = confirm_field("album","")
            info["track_num"] = confirm_field("track_num","")   
            info["genre"] = confirm_field("genre","") 
            info["year"] = confirm_field("year","")
            
        else: 
            if search_album == "y":
                info["title"] = matched_track.get("trackName")
                info["artist"] = artist_name
                info["album"] = album_name
                info["track_num"] = str(matched_track.get("trackNumber"))   
                info["genre"] = matched_track.get("primaryGenreName") 
                info["year"] = str(matched_track.get("releaseDate"))[:4]
            else:
                info["title"] = confirm_field("title", matched_track.get("trackName"))
                info["artist"] = confirm_field("artist", matched_track.get("artistName"))
                info["album"] = confirm_field("album", matched_track.get("collectionName"))
                info["track_num"] = confirm_field("track_num", str(matched_track.get("trackNumber")))   
                info["genre"] = confirm_field("genre", matched_track.get("primaryGenreName")) 
                info["year"] = confirm_field("year", str(matched_track.get("releaseDate"))[:4])

def confirm_field(data_type:str, api):
    print(f"{data_type} : {api}")
    decision = input(f"[ENTER] / corrected {data_type}: ")
    if decision == "":
        return str(api)
    else:
        return decision
    

def make_new_directory(song_dict):
    for title, info in song_dict.items():
        artist_clean = sanitize_filename(info["artist"])
        album_clean = sanitize_filename(info["album"])
        new_directory = os.path.join(save_path, artist_clean, album_clean)
        os.makedirs(new_directory, exist_ok=True)
        info["new_directory"] = new_directory + "/"

def metadata(song_dict):
    for title, info in song_dict.items():
        try:
            audio = EasyID3(info["path"])
            audio["title"] = info["title"]
            audio["artist"] = info["artist"]
            audio["album"] = info["album"]
            audio["tracknumber"] = info["track_num"]
            audio["albumartist"] = info["artist"]
            audio["genre"] = info["genre"]
            audio["date"] = info["year"]
            audio.save()
        except Exception as e:
            print(f"Error saving tags to {title}: {e}")

def fetch_artwork(song_dict):
    filename = "cover.jpg"
    for title, info in song_dict.items():
        response = requests.get(info["url"])
        o = response.json()
        if not o["results"]: 
            continue
        result = o["results"][0]    

        artwork_low_res = result.get("artworkUrl100")
        artwork_high_res = artwork_low_res.replace("100x100bb.jpg", "300x300bb.jpg")
        artwork_data = requests.get(artwork_high_res).content

        cover_path = info["new_directory"] + filename
        info["cover_path"] = cover_path
        with open(cover_path, 'wb') as handler:
            handler.write(artwork_data)

def sanitize_filename(name: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "")
    return name.strip()

def segregate_files(song_dict):
    for title, info in song_dict.items():
        title_clean = sanitize_filename(info["title"])
        new_path_mp3 = info["new_directory"] + title_clean + ".mp3"
        shutil.move(info["path"], new_path_mp3)
        new_path_cover = info["new_directory"] + "cover.jpg"
        shutil.move(info["cover_path"], new_path_cover)
        del info["cover_path"]


        #albo dodac inne api do wyboru i sobie wybierzasz na początku 
        #for def search -> search nearest Hints or smt



search_album = input("album mode: (y/n)")
artist_name = ""
album_name = ""
album_id = 0
album_tracks = []

search_mode()

link = input("link to YT video: ")
save_path = input("path to save file: ")


mp3_files_path = []
songs = {}

# #clear terminal 
#os.system('cls' if os.name == 'nt' else 'clear')
download(link)
convert(find(save_path, "*.webm"))

# Track processing pipeline
build_clear_dict(mp3_files_path)
create_url(songs)
search(songs)
make_new_directory(songs)
metadata(songs)
fetch_artwork(songs)
segregate_files(songs)

for webm_filepath in find(save_path,"*.webm"):
    os.remove(webm_filepath)
print("\nProcessing complete! Detailed structure output:")
print(songs)




