import yt_dlp
import ffmpeg
import os
from pathlib import Path
from mutagen.easyid3 import EasyID3

os.environ["PATH"] += os.pathsep + r"D://instalki//ffmpeg-8.1.2-essentials_build//ffmpeg-8.1.2-essentials_build//bin"

link = input("link to YT video")
save_path = input("path to save file")
mp3_files_path = []
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

def convert(file_path):
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
        
def metadata(file_path):
    for file in file_path:
        song_title = str(os.path.basename(file))
        song_title = os.path.splitext(song_title)[0]
        audio = EasyID3(file)
        audio["title"] = song_title

        audio.save()    
        print(audio.pprint())
        print("-" * 30)

#print(dict(enumerate(os.scandir(save_path))))
#print(find(save_path,"*.webm")) 

found_files = find(save_path,"*.webm")
convert(found_files)
metadata(mp3_files_path)

