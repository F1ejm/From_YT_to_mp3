import yt_dlp
import ffmpeg
import os
import json
import requests
import urllib.parse
from pathlib import Path
from mutagen.easyid3 import EasyID3

os.environ["PATH"] += os.pathsep + r"D://instalki//ffmpeg-8.1.2-essentials_build//ffmpeg-8.1.2-essentials_build//bin"

link = input("link to YT video")
save_path = input("path to save file")
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
        songs.update({song_title : [file]})

        audio = EasyID3(file)
        audio["title"] = song_title
        audio.save()   

        print(audio.pprint())
        print("-" * 30)
    return songs

def search_prep(song_dict):

    for title, info in song_dict.items():
        base_url = "https://itunes.apple.com/search?"
        # title = str(title).replace(" ","+")

        paremeters = {"term": title, "media": "music", "entity": "song", "limit": 1 }

        url = base_url + urllib.parse.urlencode(paremeters)
        url = str(url).replace(" ","+")

        songs[title].append(url)

# def search(song_dict):

def metadata(song_dict):
    filename = "cover.jpg"
    for title , info in song_dict.items():
        response = requests.get(info[1])
        o = response.json()
        result = o["results"][0]
        title = result.get("trackName")
        artist = result.get("artistName")
        album = result.get("collectionName")
        track_num = str(result.get("trackCount"))    
        genre = result.get("primaryGenreName") 
        year = str(result.get("releaseDate"))[:4]
        artwork_low_res = result.get("artworkUrl100")
        artwork_high_res = artwork_low_res.replace("100x100bb.jpg", "300x300bb.jpg")

        artwork_data = requests.get(artwork_high_res).content

        with open(filename, 'wb') as handler:
            handler.write(artwork_data)

        
        audio = EasyID3(info[0])
        audio["title"] = title
        audio["artist"] = artist
        audio["album"] = album
        audio["tracknumber"] = track_num
        audio["albumartist"] = artist
        audio["genre"] = genre
        audio["date"] = year
        audio.save()


#album cover and folder makeing -> next step

convert(find(save_path,"*.webm"))

#clear terminal 
os.system('cls' if os.name == 'nt' else 'clear')

build_clear_dict(mp3_files_path)
search_prep(songs)
print(songs)
metadata(songs)


