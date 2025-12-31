"""Tests for XML parser."""

from datetime import date
from pathlib import Path

import pytest

from rekordbox_collection_reader.parser import _decode_location, parse_collection

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEST_COLLECTION_PATH = FIXTURES_DIR / "test_collection.xml"


class TestParseCollection:
    """Tests for parse_collection function."""

    @pytest.fixture
    def collection(self):
        return parse_collection(TEST_COLLECTION_PATH)

    def test_parses_successfully(self, collection):
        assert collection is not None

    def test_product_info(self, collection):
        assert collection.product_name == "rekordbox"
        assert collection.product_version == "6.8.5"

    def test_correct_track_count(self, collection):
        assert len(collection.tracks) == 15

    def test_track_lookup_by_id(self, collection):
        # Track ID 1 should be Deadmau5 - Strobe
        track = collection.tracks[1]
        assert track.name == "Strobe (Original Mix)"
        assert track.artist == "Deadmau5"

    def test_track_metadata(self, collection):
        track = collection.tracks[1]
        assert track.genre == "Progressive House"
        assert track.bpm == 128.0
        assert track.key == "Fm"
        assert track.duration == 637
        assert track.play_count == 50
        assert track.rating == 255
        assert track.kind == "WAV File"
        assert track.year == 2009
        assert track.label == "Mau5trap"
        assert track.composer == "Joel Zimmerman"

    def test_url_decoding(self, collection):
        # Track 1 has URL-encoded path with %20
        track = collection.tracks[1]
        assert "Music Library" in track.location  # %20 -> space
        assert "%20" not in track.location

    def test_url_decoding_multiple_spaces(self, collection):
        # Track 4 (Armin) has multiple URL-encoded spaces
        track = collection.tracks[4]
        assert "Armin van Buuren" in track.location
        assert "%20" not in track.location

    def test_xml_entity_decoding(self, collection):
        # Track 6 (Fisher) has &amp; in label
        track = collection.tracks[6]
        assert track.label == "Catch & Release"
        assert "&amp;" not in track.label

    def test_xml_entity_in_artist(self, collection):
        # Track 8 (Above & Beyond) has &amp; in artist name
        track = collection.tracks[8]
        assert track.artist == "Above & Beyond"
        assert "&amp;" not in track.artist

    def test_date_added_parsing(self, collection):
        track = collection.tracks[1]
        assert track.date_added == date(2020, 1, 15)

    def test_track_with_no_cue_points(self, collection):
        # Track 4 (Armin) has only TEMPO, no POSITION_MARK
        track = collection.tracks[4]
        assert len(track.cue_points) == 0
        assert len(track.tempos) == 1

    def test_track_with_memory_cues_only(self, collection):
        # Track 2 (Adam Beyer) has only memory cues (Num="-1")
        track = collection.tracks[2]
        assert len(track.memory_cues) == 3
        assert len(track.hot_cues) == 0

    def test_track_with_hot_cues(self, collection):
        # Track 3 (Charlotte de Witte) has numbered hot cues
        track = collection.tracks[3]
        assert len(track.hot_cues) == 4
        hot_cue_nums = [cue.num for cue in track.hot_cues]
        assert 0 in hot_cue_nums
        assert 1 in hot_cue_nums
        assert 2 in hot_cue_nums
        assert 3 in hot_cue_nums

    def test_hot_cue_colors(self, collection):
        track = collection.tracks[3]
        cue = next(c for c in track.hot_cues if c.num == 0)
        assert cue.red == 40
        assert cue.green == 226
        assert cue.blue == 20
        assert cue.color_hex == "#28e214"

    def test_tempo_parsing(self, collection):
        track = collection.tracks[1]
        assert len(track.tempos) == 1
        tempo = track.tempos[0]
        assert tempo.bpm == 128.0
        assert tempo.inizio == 0.043
        assert tempo.metro == "4/4"
        assert tempo.battito == 1

    def test_various_file_formats(self, collection):
        formats = {track.kind for track in collection.tracks.values()}
        assert "WAV File" in formats
        assert "AIFF File" in formats
        assert "MP3 File" in formats
        assert "FLAC File" in formats

    def test_empty_string_fields(self, collection):
        # Track 3 has empty Album
        track = collection.tracks[3]
        assert track.album == ""

    def test_comments_field(self, collection):
        # Track 1 has a comment
        track = collection.tracks[1]
        assert track.comments == "Classic progressive track"

        # Track 3 has empty comments
        track3 = collection.tracks[3]
        assert track3.comments == ""


class TestPlaylistParsing:
    """Tests for playlist parsing."""

    @pytest.fixture
    def collection(self):
        return parse_collection(TEST_COLLECTION_PATH)

    def test_root_node(self, collection):
        assert collection.playlists.name == "ROOT"
        assert collection.playlists.is_folder

    def test_top_level_playlists(self, collection):
        # ROOT has 5 children: Favorites, Genres (folder), Empty Playlist, High Energy, Chill Vibes
        assert len(collection.playlists.children) == 5

    def test_playlist_track_keys(self, collection):
        # Find "Favorites" playlist
        favorites = collection.playlists.find_playlist("Favorites")
        assert favorites is not None
        assert favorites.track_keys == [1, 6, 13]

    def test_nested_folder(self, collection):
        # "Genres" is a folder containing playlists
        genres_folder = next(
            (c for c in collection.playlists.children if c.name == "Genres"),
            None,
        )
        assert genres_folder is not None
        assert genres_folder.is_folder
        assert len(genres_folder.children) == 3

    def test_deeply_nested_playlist(self, collection):
        # "Main Room" is inside Genres -> Trance Collection
        main_room = collection.playlists.find_playlist("Main Room")
        assert main_room is not None
        assert main_room.track_keys == [4, 8, 1]

    def test_empty_playlist(self, collection):
        empty = collection.playlists.find_playlist("Empty Playlist")
        assert empty is not None
        assert empty.track_keys == []
        assert len(empty.track_keys) == 0

    def test_iter_playlists(self, collection):
        playlists = list(collection.playlists.iter_playlists())
        playlist_names = [p.name for p in playlists]

        # Should include all playlists (not folders)
        assert "Favorites" in playlist_names
        assert "Techno Tracks" in playlist_names
        assert "House Tracks" in playlist_names
        assert "Main Room" in playlist_names
        assert "Empty Playlist" in playlist_names
        assert "High Energy" in playlist_names
        assert "Chill Vibes" in playlist_names

        # Should not include folders
        assert "ROOT" not in playlist_names
        assert "Genres" not in playlist_names
        assert "Trance Collection" not in playlist_names

    def test_find_nonexistent_playlist(self, collection):
        result = collection.playlists.find_playlist("Does Not Exist")
        assert result is None


class TestDecodeLocation:
    """Tests for _decode_location helper."""

    def test_basic_url_decode(self):
        location = "file://localhost/Users/test/Music%20Library/track.wav"
        result = _decode_location(location)
        assert result == "/Users/test/Music Library/track.wav"

    def test_multiple_encoded_chars(self):
        location = "file://localhost/Users/test/My%20Music%20Files/Artist%20-%20Track.wav"
        result = _decode_location(location)
        assert result == "/Users/test/My Music Files/Artist - Track.wav"

    def test_no_encoding(self):
        location = "file://localhost/Users/test/Music/track.wav"
        result = _decode_location(location)
        assert result == "/Users/test/Music/track.wav"

    def test_path_without_prefix(self):
        # Edge case: path without file://localhost prefix
        location = "/Users/test/Music/track.wav"
        result = _decode_location(location)
        assert result == "/Users/test/Music/track.wav"

    def test_special_characters(self):
        location = "file://localhost/Users/test/Music/Track%20%28Original%20Mix%29.wav"
        result = _decode_location(location)
        assert result == "/Users/test/Music/Track (Original Mix).wav"


class TestFileErrors:
    """Tests for error handling."""

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_collection("/nonexistent/path/collection.xml")

    def test_accepts_path_object(self):
        # Should work with Path objects
        collection = parse_collection(Path(TEST_COLLECTION_PATH))
        assert collection is not None

    def test_accepts_string(self):
        # Should work with string paths
        collection = parse_collection(str(TEST_COLLECTION_PATH))
        assert collection is not None
