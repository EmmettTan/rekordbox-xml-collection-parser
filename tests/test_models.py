"""Tests for Pydantic models."""

from datetime import date

import pytest

from rekordbox_collection_reader.models import (
    CAMELOT_KEYS,
    Collection,
    PlaylistNode,
    PositionMark,
    Tempo,
    Track,
)


class TestTempo:
    """Tests for Tempo model."""

    def test_tempo_creation(self):
        tempo = Tempo(inizio=0.043, bpm=128.0, metro="4/4", battito=1)
        assert tempo.inizio == 0.043
        assert tempo.bpm == 128.0
        assert tempo.metro == "4/4"
        assert tempo.battito == 1

    def test_tempo_defaults(self):
        tempo = Tempo(inizio=0.0, bpm=120.0)
        assert tempo.metro == "4/4"
        assert tempo.battito == 1


class TestPositionMark:
    """Tests for PositionMark model."""

    def test_hot_cue_creation(self):
        cue = PositionMark(
            name="Drop",
            type=0,
            start=64.0,
            num=0,
            red=40,
            green=226,
            blue=20,
        )
        assert cue.name == "Drop"
        assert cue.start == 64.0
        assert cue.num == 0
        assert cue.is_hot_cue
        assert not cue.is_memory_cue

    def test_memory_cue_creation(self):
        cue = PositionMark(name="", type=0, start=30.0, num=-1)
        assert cue.num == -1
        assert cue.is_memory_cue
        assert not cue.is_hot_cue

    def test_color_hex(self):
        cue = PositionMark(
            name="Test",
            type=0,
            start=0.0,
            num=0,
            red=40,
            green=226,
            blue=20,
        )
        assert cue.color_hex == "#28e214"

    def test_color_hex_none_when_missing(self):
        cue = PositionMark(name="Test", type=0, start=0.0, num=0)
        assert cue.color_hex is None

    def test_color_hex_partial_colors(self):
        # Only red set, should return None
        cue = PositionMark(name="Test", type=0, start=0.0, num=0, red=255)
        assert cue.color_hex is None

    def test_defaults(self):
        cue = PositionMark(start=10.0, num=1)
        assert cue.name == ""
        assert cue.type == 0
        assert cue.red is None
        assert cue.green is None
        assert cue.blue is None


class TestTrack:
    """Tests for Track model."""

    @pytest.fixture
    def sample_track(self):
        return Track(
            track_id=1,
            name="Test Track",
            artist="Test Artist",
            album="Test Album",
            genre="Techno",
            bpm=130.0,
            key="Gm",
            duration=360,
            location="/Users/test/Music/test.wav",
            date_added=date(2020, 1, 15),
            play_count=10,
            rating=255,
            kind="WAV File",
            size=50000000,
            bit_rate=1411,
            sample_rate=44100,
            comments="Test comment",
            label="Test Label",
            remixer="",
            composer="",
            grouping="",
            mix="",
            year=2020,
            disc_number=1,
            track_number=5,
            tempos=[Tempo(inizio=0.001, bpm=130.0)],
            cue_points=[
                PositionMark(name="Intro", type=0, start=0.0, num=0, red=40, green=226, blue=20),
                PositionMark(name="Drop", type=0, start=64.0, num=1, red=40, green=226, blue=20),
                PositionMark(name="", type=0, start=128.0, num=-1),
            ],
        )

    def test_track_creation(self, sample_track):
        assert sample_track.track_id == 1
        assert sample_track.name == "Test Track"
        assert sample_track.artist == "Test Artist"
        assert sample_track.bpm == 130.0
        assert sample_track.key == "Gm"

    def test_hot_cues_property(self, sample_track):
        hot_cues = sample_track.hot_cues
        assert len(hot_cues) == 2
        assert all(cue.num >= 0 for cue in hot_cues)

    def test_memory_cues_property(self, sample_track):
        memory_cues = sample_track.memory_cues
        assert len(memory_cues) == 1
        assert all(cue.num == -1 for cue in memory_cues)

    def test_camelot_key(self, sample_track):
        assert sample_track.camelot_key == "6A"

    def test_camelot_key_unknown(self):
        track = Track(
            track_id=1,
            name="Test",
            key="Unknown",
            location="/test.wav",
            date_added=date(2020, 1, 1),
        )
        assert track.camelot_key == ""

    def test_duration_formatted(self, sample_track):
        assert sample_track.duration_formatted == "6:00"

    def test_duration_formatted_with_seconds(self):
        track = Track(
            track_id=1,
            name="Test",
            duration=185,
            location="/test.wav",
            date_added=date(2020, 1, 1),
        )
        assert track.duration_formatted == "3:05"

    def test_star_rating_5_stars(self, sample_track):
        assert sample_track.star_rating == 5

    def test_star_rating_0_stars(self):
        track = Track(
            track_id=1,
            name="Test",
            rating=0,
            location="/test.wav",
            date_added=date(2020, 1, 1),
        )
        assert track.star_rating == 0

    def test_star_rating_3_stars(self):
        track = Track(
            track_id=1,
            name="Test",
            rating=153,
            location="/test.wav",
            date_added=date(2020, 1, 1),
        )
        assert track.star_rating == 3

    def test_defaults(self):
        track = Track(
            track_id=1,
            name="Test",
            location="/test.wav",
            date_added=date(2020, 1, 1),
        )
        assert track.artist == ""
        assert track.album == ""
        assert track.genre == ""
        assert track.bpm == 0.0
        assert track.play_count == 0
        assert track.rating == 0
        assert track.tempos == []
        assert track.cue_points == []


class TestPlaylistNode:
    """Tests for PlaylistNode model."""

    def test_playlist_creation(self):
        playlist = PlaylistNode(
            name="My Playlist",
            node_type=1,
            track_keys=[1, 2, 3],
        )
        assert playlist.name == "My Playlist"
        assert playlist.is_playlist
        assert not playlist.is_folder
        assert playlist.track_keys == [1, 2, 3]

    def test_folder_creation(self):
        folder = PlaylistNode(
            name="My Folder",
            node_type=0,
            children=[
                PlaylistNode(name="Nested Playlist", node_type=1, track_keys=[4, 5]),
            ],
        )
        assert folder.name == "My Folder"
        assert folder.is_folder
        assert not folder.is_playlist
        assert len(folder.children) == 1

    def test_iter_playlists(self):
        root = PlaylistNode(
            name="ROOT",
            node_type=0,
            children=[
                PlaylistNode(name="Playlist 1", node_type=1, track_keys=[1]),
                PlaylistNode(
                    name="Folder",
                    node_type=0,
                    children=[
                        PlaylistNode(name="Playlist 2", node_type=1, track_keys=[2]),
                        PlaylistNode(name="Playlist 3", node_type=1, track_keys=[3]),
                    ],
                ),
            ],
        )
        playlists = list(root.iter_playlists())
        assert len(playlists) == 3
        assert [p.name for p in playlists] == ["Playlist 1", "Playlist 2", "Playlist 3"]

    def test_find_playlist_top_level(self):
        root = PlaylistNode(
            name="ROOT",
            node_type=0,
            children=[
                PlaylistNode(name="Target", node_type=1, track_keys=[1, 2]),
            ],
        )
        result = root.find_playlist("Target")
        assert result is not None
        assert result.name == "Target"

    def test_find_playlist_nested(self):
        root = PlaylistNode(
            name="ROOT",
            node_type=0,
            children=[
                PlaylistNode(
                    name="Folder",
                    node_type=0,
                    children=[
                        PlaylistNode(
                            name="Subfolder",
                            node_type=0,
                            children=[
                                PlaylistNode(name="Deep Playlist", node_type=1, track_keys=[1]),
                            ],
                        ),
                    ],
                ),
            ],
        )
        result = root.find_playlist("Deep Playlist")
        assert result is not None
        assert result.name == "Deep Playlist"

    def test_find_playlist_not_found(self):
        root = PlaylistNode(
            name="ROOT",
            node_type=0,
            children=[
                PlaylistNode(name="Other", node_type=1, track_keys=[1]),
            ],
        )
        result = root.find_playlist("NonExistent")
        assert result is None

    def test_defaults(self):
        node = PlaylistNode(name="Test", node_type=1)
        assert node.track_keys == []
        assert node.children == []


class TestCollection:
    """Tests for Collection model."""

    def test_collection_creation(self):
        collection = Collection(
            product_name="rekordbox",
            product_version="6.8.5",
            tracks={
                1: Track(
                    track_id=1,
                    name="Track 1",
                    location="/test.wav",
                    date_added=date(2020, 1, 1),
                ),
            },
            playlists=PlaylistNode(name="ROOT", node_type=0),
        )
        assert collection.product_name == "rekordbox"
        assert collection.product_version == "6.8.5"
        assert len(collection.tracks) == 1
        assert 1 in collection.tracks

    def test_defaults(self):
        collection = Collection(
            playlists=PlaylistNode(name="ROOT", node_type=0),
        )
        assert collection.product_name == "rekordbox"
        assert collection.product_version == ""
        assert collection.tracks == {}


class TestCamelotKeys:
    """Tests for Camelot key mapping."""

    def test_all_minor_keys_mapped(self):
        minor_keys = ["Abm", "Ebm", "Bbm", "Fm", "Cm", "Gm", "Dm", "Am", "Em", "Bm", "F#m", "Dbm"]
        for key in minor_keys:
            assert key in CAMELOT_KEYS
            assert CAMELOT_KEYS[key].endswith("A")

    def test_all_major_keys_mapped(self):
        major_keys = ["B", "F#", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E"]
        for key in major_keys:
            assert key in CAMELOT_KEYS
            assert CAMELOT_KEYS[key].endswith("B")

    def test_common_keys(self):
        assert CAMELOT_KEYS["Am"] == "8A"
        assert CAMELOT_KEYS["C"] == "8B"
        assert CAMELOT_KEYS["Fm"] == "4A"
        assert CAMELOT_KEYS["Ab"] == "4B"
