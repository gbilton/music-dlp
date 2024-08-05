from datetime import datetime
import os
import shlex
import subprocess

from config import MUSIC_PATH
from enums import StatusEnum, TuningEnum
from models import Song


class SongProcessing:

    tuning_map = {
        TuningEnum.E: "std",
        TuningEnum.Eb: "eb"
    }

    def __init__(self):
        self.base_path = MUSIC_PATH

    def refresh(self, song: Song):
        artist_path = self.create_artist_path(artist_name=song.artist.name)

        if not song.converted_song_path or not song.downloaded_song_path:
            song_paths = self.create_song_paths(song_name=song.name, tuning=song.original_tuning)
            song.converted_song_path = os.path.join(artist_path, song_paths.get("converted_song_path"))
            song.downloaded_song_path = os.path.join(artist_path, song_paths.get("downloaded_song_path"))

        download_success = self.download_audio(song_path=song.downloaded_song_path, url=song.link)
        if download_success.get("status", 500) == 200:
            song.saved_downloaded = True
        else:
            song.status = StatusEnum.ERROR
            song.updated_at = datetime.now()
            return song
            
        pitch_value = self._get_pitch_value(original_tuning=song.original_tuning)
        convert_success = self.convert_tuning(
            original_audio_path=song.downloaded_song_path,
            processed_audio_path=song.converted_song_path, 
            pitch_value=pitch_value,
            )
        if convert_success.get("status", 500) == 200:
            song.saved_converted = True
        else:
            song.status = StatusEnum.ERROR
            song.updated_at = datetime.now()
            return song

        song.status = StatusEnum.SUCCESS
        song.updated_at = datetime.now()

        return song
        
        
    def download_audio(self, song_path: str, url: str):
        try:
            # Download audio using yt-dlp with verbose output
            download_command = f"yt-dlp -x --audio-format mp3 -o {song_path} {shlex.quote(url)} --verbose"
            download_result = subprocess.run(shlex.split(download_command), check=True, capture_output=True, text=True)
            print(download_result.stdout)  # Print verbose output
            return {"detail": "Audio downloaded successfully", "song_path": song_path, "status": 200}
        except subprocess.CalledProcessError as e:
            return {"detail": "Audio download failed", "error": e.stderr, "status": 500}
        except Exception as e:
            return {"detail": "An unexpected error occurred", "error": str(e), "status": 500}

    def convert_tuning(self, original_audio_path: str, processed_audio_path: str, pitch_value: int):
        try:
            # Process audio with sox
            sox_command = f"sox {original_audio_path} {processed_audio_path} pitch {pitch_value}"
            sox_result = subprocess.run(shlex.split(sox_command), check=True, capture_output=True, text=True)
            print(sox_result.stdout)  # Print sox output
            return {"detail": "Audio conversion successful", "processed_audio_path": processed_audio_path, "status": 200}
        except subprocess.CalledProcessError as e:
            return {"detail": "Audio conversion failed", "error": e.stderr, "status": 500}
        except Exception as e:
            return {"detail": "An unexpected error occurred", "error": str(e), "status": 500}

    def create_artist_path(self, artist_name: str):
        parsed_artist_name = self._parse_name(artist_name)
        artist_path = os.path.join(self.base_path, parsed_artist_name)
        os.makedirs(artist_path, exist_ok=True)
        return artist_path

    def create_song_paths(self, song_name: str, tuning: TuningEnum):
        parsed_song_name = self._parse_name(song_name)
        parsed_tuning = self._parse_tuning(tuning)
        parsed_other_tuning = self._parse_tuning(self._get_other_tuning(tuning))

        return {
            "downloaded_song_path": parsed_song_name + "-" + parsed_tuning + ".mp3",
            "converted_song_path": parsed_song_name + "-" + parsed_other_tuning + ".mp3",
        }

    def _parse_name(self, name: str):
        name = name.lower()
        name = name.split(" ")
        return "-".join(name)

    def _parse_tuning(self, tuning: TuningEnum):
        return self.tuning_map[tuning]

    def _get_other_tuning(self, current_tuning):
        if current_tuning == TuningEnum.E:
            return TuningEnum.Eb
        elif current_tuning == TuningEnum.Eb:
            return TuningEnum.E
        else:
            return None

    def _get_pitch_value(self, original_tuning: TuningEnum):
        if original_tuning == TuningEnum.E:
            return -100
        elif original_tuning == TuningEnum.Eb:
            return 100
            

