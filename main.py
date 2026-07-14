import yt_dlp

link = input("link to YT video")
file_path = input("path to save file")
ydl_options = {
    "format": "bestaudio", # best or worst for video 
    "outtmpl": file_path+ "/%(title)s.%(ext)s"

}

with yt_dlp.YoutubeDL(ydl_options) as ydl:
    ydl.download([link])