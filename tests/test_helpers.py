"""Tests for helper functions."""

from datetime import date
from pathlib import Path

import pytest

from rekordbox_collection_reader.helpers import (
    artists_by_track_count,
    bpm_distribution,
    filter_tracks,
    genre_counts,
    get_playlist,
    get_playlist_names,
    key_distribution,
    search,
)
from rekordbox_collection_reader.parser import parse_collection

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEST_COLLECTION_PATH = FIXTURES_DIR / "test_collection.xml"


@pytest.fixture
def collection():
    return parse_collection(TEST_COLLECTION_PATH)


class TestFilterTracks:
    """Tests for filter_tracks function."""

    def test_filter_by_genre(self, collection):
        results = filter_tracks(collection, genre="Techno")
        assert len(results) == 5  # Tracks 2, 3, 12, 14, 15 (Hard Techno is separate)
        assert all(t.genre == "Techno" for t in results)

    def test_filter_by_genre_case_insensitive(self, collection):
        results = filter_tracks(collection, genre="techno")
        assert len(results) == 5

    def test_filter_by_bpm_range(self, collection):
        results = filter_tracks(collection, bpm_range=(125, 130))
        assert len(results) == 6  # Tracks at 126, 128, 130 BPM
        assert all(125 <= t.bpm <= 130 for t in results)

    def test_filter_by_bpm_exact(self, collection):
        results = filter_tracks(collection, bpm_range=(128, 128))
        assert len(results) == 2
        assert all(t.bpm == 128.0 for t in results)

    def test_filter_by_key(self, collection):
        results = filter_tracks(collection, key="Gm")
        assert len(results) == 1
        assert results[0].artist == "Adam Beyer"

    def test_filter_by_key_case_insensitive(self, collection):
        results = filter_tracks(collection, key="gm")
        assert len(results) == 1

    def test_filter_by_artist(self, collection):
        results = filter_tracks(collection, artist="Charlotte")
        assert len(results) == 1
        assert results[0].artist == "Charlotte de Witte"

    def test_filter_by_artist_case_insensitive(self, collection):
        results = filter_tracks(collection, artist="CHARLOTTE")
        assert len(results) == 1

    def test_filter_by_artist_partial(self, collection):
        # Should match "Above & Beyond" with partial match
        results = filter_tracks(collection, artist="Above")
        assert len(results) == 1
        assert "Above" in results[0].artist

    def test_filter_by_min_play_count(self, collection):
        results = filter_tracks(collection, min_play_count=40)
        assert len(results) == 3
        assert all(t.play_count >= 40 for t in results)

    def test_filter_by_date_range(self, collection):
        results = filter_tracks(
            collection,
            date_range=(date(2020, 1, 1), date(2020, 12, 31)),
        )
        assert len(results) == 6  # Tracks 1, 2, 6, 8, 11, 14
        assert all(date(2020, 1, 1) <= t.date_added <= date(2020, 12, 31) for t in results)

    def test_filter_by_kind(self, collection):
        results = filter_tracks(collection, kind="WAV")
        assert len(results) == 6
        assert all("WAV" in t.kind for t in results)

    def test_filter_multiple_criteria(self, collection):
        # Techno tracks with BPM 140+
        results = filter_tracks(
            collection,
            genre="Techno",
            bpm_range=(140, 150),
        )
        assert len(results) == 2  # Charlotte de Witte (140) and Reinier Zonneveld (140)
        assert all(t.genre == "Techno" and t.bpm >= 140 for t in results)

    def test_filter_no_matches(self, collection):
        results = filter_tracks(collection, genre="Dubstep")
        assert len(results) == 0

    def test_filter_no_criteria_returns_all(self, collection):
        results = filter_tracks(collection)
        assert len(results) == 15


class TestSearch:
    """Tests for search function."""

    def test_search_by_track_name(self, collection):
        results = search(collection, "Strobe")
        assert len(results) == 1
        assert results[0].name == "Strobe (Original Mix)"

    def test_search_by_artist(self, collection):
        results = search(collection, "Deadmau5")
        assert len(results) == 1
        assert results[0].artist == "Deadmau5"

    def test_search_by_album(self, collection):
        results = search(collection, "Settle")
        assert len(results) == 1
        assert results[0].album == "Settle"

    def test_search_case_insensitive(self, collection):
        results = search(collection, "STROBE")
        assert len(results) == 1

    def test_search_partial_match(self, collection):
        results = search(collection, "Original")
        # Many tracks have "Original Mix" in the name
        assert len(results) > 5

    def test_search_no_matches(self, collection):
        results = search(collection, "xyz123nonexistent")
        assert len(results) == 0

    def test_search_special_characters(self, collection):
        # Search for "Above & Beyond" - the & should work
        results = search(collection, "Above & Beyond")
        assert len(results) == 1


class TestGetPlaylist:
    """Tests for get_playlist function."""

    def test_get_top_level_playlist(self, collection):
        tracks = get_playlist(collection, "Favorites")
        assert tracks is not None
        assert len(tracks) == 3
        # Check that we got actual Track objects
        assert tracks[0].track_id == 1
        assert tracks[0].name == "Strobe (Original Mix)"

    def test_get_nested_playlist(self, collection):
        tracks = get_playlist(collection, "Techno Tracks")
        assert tracks is not None
        assert len(tracks) == 6

    def test_get_deeply_nested_playlist(self, collection):
        tracks = get_playlist(collection, "Main Room")
        assert tracks is not None
        assert len(tracks) == 3

    def test_get_empty_playlist(self, collection):
        tracks = get_playlist(collection, "Empty Playlist")
        assert tracks is not None
        assert len(tracks) == 0

    def test_get_nonexistent_playlist(self, collection):
        tracks = get_playlist(collection, "Does Not Exist")
        assert tracks is None

    def test_playlist_preserves_order(self, collection):
        tracks = get_playlist(collection, "Favorites")
        assert tracks is not None
        # Order should be 1, 6, 13 as defined in XML
        assert [t.track_id for t in tracks] == [1, 6, 13]


class TestGetPlaylistNames:
    """Tests for get_playlist_names function."""

    def test_returns_all_playlists(self, collection):
        names = get_playlist_names(collection)
        assert "Favorites" in names
        assert "Techno Tracks" in names
        assert "House Tracks" in names
        assert "Main Room" in names
        assert "Empty Playlist" in names
        assert "High Energy" in names
        assert "Chill Vibes" in names

    def test_excludes_folders(self, collection):
        names = get_playlist_names(collection)
        assert "ROOT" not in names
        assert "Genres" not in names
        assert "Trance Collection" not in names

    def test_includes_nested_playlists(self, collection):
        names = get_playlist_names(collection)
        # Main Room is deeply nested
        assert "Main Room" in names


class TestGenreCounts:
    """Tests for genre_counts function."""

    def test_counts_genres(self, collection):
        counts = genre_counts(collection)
        assert "Techno" in counts
        assert counts["Techno"] == 5  # Tracks 2, 3, 12, 14, 15

    def test_sorted_by_count(self, collection):
        counts = genre_counts(collection)
        values = list(counts.values())
        assert values == sorted(values, reverse=True)

    def test_includes_all_genres(self, collection):
        counts = genre_counts(collection)
        # Check for various genres in the test data
        assert "Progressive House" in counts
        assert "Deep House" in counts
        assert "Trance" in counts


class TestBpmDistribution:
    """Tests for bpm_distribution function."""

    def test_counts_bpms(self, collection):
        dist = bpm_distribution(collection)
        assert 128.0 in dist
        assert dist[128.0] == 2  # Strobe and Pan-Pot

    def test_sorted_by_count(self, collection):
        dist = bpm_distribution(collection)
        values = list(dist.values())
        assert values == sorted(values, reverse=True)


class TestKeyDistribution:
    """Tests for key_distribution function."""

    def test_counts_keys(self, collection):
        dist = key_distribution(collection)
        assert "Fm" in dist
        assert dist["Fm"] == 1  # Strobe

    def test_sorted_by_count(self, collection):
        dist = key_distribution(collection)
        values = list(dist.values())
        assert values == sorted(values, reverse=True)


class TestArtistsByTrackCount:
    """Tests for artists_by_track_count function."""

    def test_returns_tuples(self, collection):
        artists = artists_by_track_count(collection)
        assert all(isinstance(item, tuple) for item in artists)
        assert all(len(item) == 2 for item in artists)

    def test_sorted_by_count(self, collection):
        artists = artists_by_track_count(collection)
        counts = [count for _, count in artists]
        assert counts == sorted(counts, reverse=True)

    def test_includes_all_artists(self, collection):
        artists = artists_by_track_count(collection)
        artist_names = [name for name, _ in artists]
        assert "Deadmau5" in artist_names
        assert "Charlotte de Witte" in artist_names
        assert "Eric Prydz" in artist_names
