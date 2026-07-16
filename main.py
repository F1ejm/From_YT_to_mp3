import yt_dlp
import ffmpeg

link = input("link to YT video")
save_path = input("path to save file")
ydl_options = {
    "format": "bestaudio", # best or worst for video 
    "outtmpl": save_path+ "/%(title)s.%(ext)s"

}

with yt_dlp.YoutubeDL(ydl_options) as ydl:
    ydl.download([link])



def convert(file_path):
    input_file = ffmpeg.input(file_path)
    output_audio = ffmpeg.output(input_file, "D:\git PROJEKTY\scraping_PY")
    ffmpeg.run(output_audio)