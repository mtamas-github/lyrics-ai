import unittest
import pytest
from unittest.mock import MagicMock, patch
from lyricsai.models import Song, Artist
from lyricsai.process_flow import process


class TestProcessFlow(unittest.TestCase):

    @patch('lyricsai.process_flow.MusixmatchAPI')
    @patch('lyricsai.process_flow.OpenAIAPI')
    def test_process_with_no_song(self, MockOpenAIAPI, MockMusixmatchAPI):
        """Test processing with a None song object."""
        result = process(None)
        self.assertFalse(result)

    @pytest.mark.django_db
    @patch('lyricsai.process_flow.MusixmatchAPI')
    @patch('lyricsai.process_flow.OpenAIAPI')
    def test_process_with_musixmatch_error(self, MockOpenAIAPI, MockMusixmatchAPI):
        """Test processing when MusixmatchAPI raises an error."""
        # Mock song object
        # Create a real Artist instance
        artist = Artist.objects.create(name='Artist Name')

        # Create a Song instance with the real artist
        song = Song.objects.create(artist=artist, title='Song Title')
        song.save = MagicMock()

        # Mock MusixmatchAPI behavior
        mock_musixmatch = MockMusixmatchAPI.return_value
        mock_musixmatch.search_track.side_effect = ValueError("Musixmatch API error")

        result = process(song)

        # Assert the song's error field is set and saved
        song.save.assert_called_once()
        self.assertEqual(song.error, "Musixmatch API error")

    @pytest.mark.django_db
    @patch('lyricsai.process_flow.MusixmatchAPI')
    @patch('lyricsai.process_flow.OpenAIAPI')
    def test_process_with_lyrics_found(self, MockOpenAIAPI, MockMusixmatchAPI):
        """Test processing when lyrics are found."""
        # Create a real Artist instance
        artist = Artist.objects.create(name='Artist Name')

        # Create a Song instance with the real artist
        song = Song.objects.create(artist=artist, title='Song Title')
        song.save = MagicMock()  # Mock the save method to avoid interacting with the database during the test

        # Mock MusixmatchAPI behavior
        mock_musixmatch = MockMusixmatchAPI.return_value
        mock_musixmatch.search_track.return_value = 12345
        mock_musixmatch.get_track_lyrics.return_value = "These are sample lyrics"

        # Mock OpenAIAPI behavior
        mock_openai = MockOpenAIAPI.return_value
        mock_openai.analyze_lyrics = MagicMock()
        mock_openai.error = None
        mock_openai.summary = "Sample summary"
        mock_openai.countries = ["Country1", "Country2"]

        # Call the function to test
        from lyricsai.process_flow import process
        process(song)

        # Assert lyrics were saved and OpenAI was called
        song.save.assert_called()
        self.assertEqual(song.lyrics, "These are sample lyrics")
        self.assertEqual(song.summary, "Sample summary")
        self.assertEqual(song.countries, '["Country1", "Country2"]')

    @pytest.mark.django_db
    @patch('lyricsai.process_flow.MusixmatchAPI')
    @patch('lyricsai.process_flow.OpenAIAPI')
    def test_process_with_openai_error(self, MockOpenAIAPI, MockMusixmatchAPI):
        """Test processing when OpenAIAPI raises an error."""
        # Mock song object
        # Create a real Artist instance
        artist = Artist.objects.create(name='Artist Name')

        # Create a Song instance with the real artist
        song = Song.objects.create(artist=artist, title='Song Title')
        song.save = MagicMock()

        # Mock MusixmatchAPI behavior
        mock_musixmatch = MockMusixmatchAPI.return_value
        mock_musixmatch.search_track.return_value = 12345
        mock_musixmatch.get_track_lyrics.return_value = "These are sample lyrics"

        # Mock OpenAIAPI behavior
        mock_openai = MockOpenAIAPI.return_value
        mock_openai.analyze_lyrics = MagicMock()
        mock_openai.error = "OpenAI API error"

        result = process(song)

        # Assert the error was set and saved
        song.save.assert_called()
        self.assertEqual(song.error, "OpenAI API error")
