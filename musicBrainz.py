
import yt_dlp
import os
import musicbrainzngs
from pathlib import Path



def download_vid(link):
    ydl_options = {
        "format": "bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": str(save_path) + "/%(title)s.%(ext)s",
        "quiet": "true",
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web", "tv"],
            }
        }
    }

    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.download([link])

def find_downloaded(path, ext):
    find = []
    for file in Path(path).rglob(ext):
        find.append(str(file))
        return find

def search():
    result = musicbrainzngs.search_artists(artist= artist, limit=5)
    for a in result["artist-list"]:
        print(a["id"], a["name"], a.get("disambiguation", ""))


def make_dict(files):
    for file in files:
        song_title = str(os.path.basename(file))
        song_title = os.path.splitext(song_title)[0]
        songs.update({song_title : {"path":file}})
        songs[song_title]["artist_name"] = artist

def search_album():
    result = musicbrainzngs.search_releases(artist=artist)
    for a in result["release-list"]:
        list = a["artist-credit"]
        if find_in_list(list,artist) and a["status"] != "Bootleg":
            print(a["title"], a["status"])   
        

def find_in_list(list:list,target:str):
    for entry in list:
        if not isinstance(entry, dict):
            continue                       
        name = entry["artist"]["name"]
        if name.lower() == target.lower():
            return True
    return False

songs = {}
album = ""
artist = "Cocteau Twins"
save_path = "D://git PROJEKTY//scraping_PY//outputs"

musicbrainzngs.set_useragent(
    "musicserach",      # app name
    "0.1",             # version
    "email@gmail.com"   # email 
)

download_vid("https://www.youtube.com/watch?v=qgffvFM1J-Q")
files = find_downloaded(save_path, "*.mp4")
print(files)
search()
artist = str(input("paste artist name: "))
make_dict(files)
search_album()



print(songs)

