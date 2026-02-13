import sys
import os
import yt_dlp
from moviepy import VideoFileClip
from pydub import AudioSegment

# Add FFmpeg path (no system PATH needed)
ffmpeg_path = r"C:\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

def download_videos(singer, num_videos):
    print("Downloading videos...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'ignoreerrors': True   # ✅ VERY IMPORTANT
    }

    downloaded_files = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_query = f"ytsearch{num_videos}:{singer} songs"
        result = ydl.extract_info(search_query, download=True)

        if result and 'entries' in result:
            for entry in result['entries']:
                if entry:
                    filename = f"video_{entry['id']}.{entry['ext']}"
                    downloaded_files.append(filename)

    return downloaded_files


def convert_to_audio(video_files):
    print("Converting videos to audio...")
    audio_files = []

    for video in video_files:
        clip = VideoFileClip(video)
        audio_file = video.replace(".mp4", ".mp3")
        clip.audio.write_audiofile(audio_file)
        clip.close()
        audio_files.append(audio_file)

    return audio_files


def trim_audio(audio_files, duration):
    print("Trimming audio files...")
    trimmed_files = []

    for file in audio_files:
        audio = AudioSegment.from_file(file)
        trimmed = audio[:duration * 1000]
        trimmed.export(file, format="mp3")
        trimmed_files.append(file)

    return trimmed_files


def merge_audio(audio_files, output_name):
    print("Merging audio files...")
    combined = AudioSegment.empty()

    for file in audio_files:
        audio = AudioSegment.from_mp3(file)
        combined += audio

    combined.export(output_name, format="mp3")
    print(f"Final mashup saved as {output_name}")


def cleanup(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


# ✅ MAIN FUNCTION FOR FLASK
def generate_mashup(singer, num_videos, duration, output_name):
    if num_videos <= 1:
        raise ValueError("NumberOfVideos must be greater than 1.")


    if duration <= 20:
        raise ValueError("AudioDuration must be greater than 20 seconds.")

    videos = download_videos(singer, num_videos)
    audios = convert_to_audio(videos)
    trimmed = trim_audio(audios, duration)
    merge_audio(trimmed, output_name)

    cleanup(videos)
    cleanup(audios)


# ✅ Optional CLI Support
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python 102303460.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer = sys.argv[1]
    count = int(sys.argv[2])
    duration = int(sys.argv[3])
    output_name = sys.argv[4]

    generate_mashup(singer, count, duration, output_name)
