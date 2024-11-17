"""This file is for managing multiple api calls and processing the data."""
from lyricsai.models import Song
from lyricsai.musixmatch import MusixmatchAPI
from lyricsai.openai import OpenAIAPI
import json

def process(song: Song) -> bool:
    """Process the song data.

    :param song: The song object to process.
    """
    if not song:
        return False

    # Find the lyrics from the Musixmatch API
    musixmatch = MusixmatchAPI()
    try:
        song_track_id = musixmatch.search_track(song.artist.name, song.title)
    except ValueError as e:
        song.error = str(e)
        song.save()
    else:
        try:
            lyrics = musixmatch.get_track_lyrics(song_track_id)
        except ValueError as e:
            song.error = str(e)
            song.save()
        else:
            song.lyrics = lyrics
            song.save()

    if song.lyrics:
        # Process the lyrics with OpenAI
        lyrics_ai = OpenAIAPI()
        lyrics_ai.analyze_lyrics(song.lyrics)
        if lyrics_ai.error:
            song.error = lyrics_ai.error
        else:
            song.summary = lyrics_ai.summary
            song.countries = json.dumps(lyrics_ai.countries)
        song.save()

