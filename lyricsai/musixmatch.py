import requests
from decouple import config

class MusixmatchAPI:
    BASE_URL = "https://api.musixmatch.com/ws/1.1/"

    def __init__(self):
        self.api_key = config("MUSIXMATCH_API_KEY")

    def search_track(self, artist: str, title: str) -> int:
        """
        Searches for a track using the provided artist and title.

        :param: artist The name of the artist.
        :param: title The title of the song.
        :return: track_id of the matched track.
        :raises: ValueError if the track is not found or the response is invalid.
        """
        endpoint = f"{self.BASE_URL}matcher.track.get"
        params = {
            "q_artist": artist,
            "q_track": title,
            "apikey": self.api_key
        }
        response = requests.get(endpoint, params=params)
        response_data = response.json()
        try:
            track_id = response_data["message"]["body"]["track"]["track_id"]
            return track_id
        except (KeyError, TypeError) as e:
            print(e)
            raise ValueError("Track not found or invalid response.")

    def get_track_lyrics(self, track_id: int) -> str:
        """
        Retrieves lyrics for the specified track ID.

        :param: track_id The ID of the track.
        :return: The lyrics of the track.
        """
        endpoint = f"{self.BASE_URL}track.lyrics.get"
        params = {
            "track_id": track_id,
            "apikey": self.api_key
        }
        response = requests.get(endpoint, params=params)
        response_data = response.json()
        try:
            lyrics = response_data["message"]["body"]["lyrics"]["lyrics_body"]
            return lyrics
        except (KeyError, TypeError) as e:
            print(e)
            raise ValueError("Lyrics not found or invalid response.")
