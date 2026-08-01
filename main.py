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

link = input("link to YT video: ")
save_path = input("path to save file: ")
mp3_files_path = []
songs = {

}

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
        songs.update({song_title : {"path":file}})

        audio = EasyID3(file)
        audio["title"] = song_title
        audio.save()   

        # print(audio.pprint())
        # print("-" * 30)
    return songs

def search_prep(song_dict):

    for title, info in song_dict.items():
        base_url = "https://itunes.apple.com/search?"
        # title = str(title).replace(" ","+")

        paremeters = {"term": title, "media": "music", "entity": "song", "limit": 1 }

        url = base_url + urllib.parse.urlencode(paremeters)
        url = str(url).replace(" ","+")

        info["url"] = url

def search(song_dict):
    for title, info in song_dict.items():
        print(title)
        print("-" * 30)
        response = requests.get(info["url"])
        o = response.json()
        result = o["results"][0]

        #for metadata
        info["title"] = confirm_field("title",result.get("trackName"))
        info["artist"] = confirm_field("artist",result.get("artistName"))
        info["album"] = confirm_field("album",result.get("collectionName"))
        info["track_num"] = confirm_field("track_num",str(result.get("trackCount")))   
        info["genre"] = confirm_field("genre",result.get("primaryGenreName")) 
        info["year"] = confirm_field("year",str(result.get("releaseDate"))[:4])

def confirm_field(data_type:str, api):
    print(f"{data_type} : {api}")
    decision = input("y / corrected title: ")
    if decision == "y":
        return api
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

        #embeded artwork dla kazdej piosenki
        #webm_file = save_path + original_title[:4] + ".webm"
        #make so webm file will be deleted at the end of proces
        #zabezpieczyc i aby mozna był zmieniac nazwy i w ogole to mozna wszystko
        #czasami wynajduje dziwne rzeczy i dodac aby mozna było na sztywno wyszukiwac po albumie albo artyście albo niczym aka jednej piosence    
        #albo dodac inne api do wyboru i sobie wybierzasz na początku 



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




