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

serach_album = input("album mode: (y/n)")
link = input("link to YT video: ")
save_path = input("path to save file: ")
mp3_files_path = []
songs = {}

ydl_options = {
    "format": "bestaudio", # best or worst for video 
    "outtmpl": save_path+ "/%(title)s.%(ext)s"
}

with yt_dlp.YoutubeDL(ydl_options) as ydl:
    ydl.download([link])


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

        # audio = EasyID3(file)
        # audio["title"] = song_title
        # audio.save()   
        # print(audio.pprint())
        # print("-" * 30)

def search_prep(song_dict):

    for title, info in song_dict.items():
        base_url = "https://itunes.apple.com/search?"
        # title = str(title).replace(" ","+")

        if serach_album == "y":
            artist = input("provide artist name to search: ")
            album_name = input("provide album name: ")
            info["url"] = base_url+search_album_info(title,artist,album_name)
        else: 
            info["url"] = base_url+search_singly(title)
        info["url"] = str(info["url"]).replace(" ","+")

def search_album_info(title:str,artist:str, album:str):
    paremeters = {"term": title + "+" + artist + "+" + album, "media": "music", "entity": "song", "limit": 1}
    return urllib.parse.urlencode(paremeters)

def search_singly(title:str):
    paremeters = {"term": title , "media": "music", "entity": "song", "limit": 1}
    return urllib.parse.urlencode(paremeters)

def search(song_dict):
    for title, info in song_dict.items():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(title)
        print("-" * 30)
        response = requests.get(info["url"])
        o = response.json()
        
        if not o["results"]: 
            print("something went horribly wrong, please fill data manualy ")
            info["title"] = confirm_field("title","")
            info["artist"] = confirm_field("artist","")
            info["album"] = confirm_field("album","")
            info["track_num"] = confirm_field("track_num","")   
            info["genre"] = confirm_field("genre","") 
            info["year"] = confirm_field("year","")
        else: 
            result = o["results"][0]
            if serach_album == "y":
                info["title"] = result.get("trackName")
                info["artist"] = result.get("artistName")
                info["album"] = result.get("collectionName")
                info["track_num"] = str(result.get("trackCount"))   
                info["genre"] = result.get("primaryGenreName") 
                info["year"] = str(result.get("releaseDate"))[:4]
            else:
                info["title"] = confirm_field("title",result.get("trackName"))
                info["artist"] = confirm_field("artist",result.get("artistName"))
                info["album"] = confirm_field("album",result.get("collectionName"))
                info["track_num"] = confirm_field("track_num",str(result.get("trackCount")))   
                info["genre"] = confirm_field("genre",result.get("primaryGenreName")) 
                info["year"] = confirm_field("year",str(result.get("releaseDate"))[:4])
        

def confirm_field(data_type:str, api):
    print(f"{data_type} : {api}")
    decision = input(f"[ENTER] / corrected {data_type}: ")
    if decision == "":
        return str(api)
    else:
        return decision
    

def make_new_directory(song_dict):
    for title, info in song_dict.items():
        new_directory = save_path + "/" + info["artist"] + "/" + info["album"] + "/"
        os.makedirs(new_directory, exist_ok=True)
        info["new_directory"] = new_directory

def metadata(song_dict):
    for title , info in song_dict.items():

        audio = EasyID3(info["path"])
        audio["title"] = info["title"]
        audio["artist"] = info["artist"]
        audio["album"] = info["album"]
        audio["tracknumber"] = info["track_num"]
        audio["albumartist"] = info["artist"]
        audio["genre"] = info["genre"]
        audio["date"] = info["year"]
        audio.save()

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

def segregate_files(song_dict):
    for title , info in song_dict.items():

        new_path_mp3 = info["new_directory"] +  info["title"] + ".mp3"
        new_path_cover = info["new_directory"] + "cover.jpg"
        shutil.move(info["path"],new_path_mp3)
        shutil.move(info["cover_path"], new_path_cover)
        del info["cover_path"]
        #new path must be updated etc. 


        #webm_file = save_path + original_title[:4] + ".webm"
        #make so webm file will be deleted at the end of proces  
        #albo dodac inne api do wyboru i sobie wybierzasz na początku 
        #for def search -> search nearest Hints or smt



#album cover and folder makeing -> next step

convert(find(save_path,"*.webm"))

#clear terminal 
os.system('cls' if os.name == 'nt' else 'clear')

build_clear_dict(mp3_files_path)
search_prep(songs)
search(songs)
make_new_directory(songs)
metadata(songs)
fetch_artwork(songs)
segregate_files(songs)

print(songs)




