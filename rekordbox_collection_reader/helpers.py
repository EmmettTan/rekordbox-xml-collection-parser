"""Helper methods for Collection analysis and querying."""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Collection, Track


class CollectionHelpers:
    """Mixin class providing helper methods for Collection.

    This class is designed to be used as a mixin with the Collection model.
    Import and call these methods with a Collection instance.
    """

    @staticmethod
    def filter_tracks(
        collection: Collection,
        *,
        genre: str | None = None,
        bpm_range: tuple[float, float] | None = None,
        key: str | None = None,
        artist: str | None = None,
        min_play_count: int | None = None,
        date_range: tuple[date, date] | None = None,
        kind: str | None = None,
    ) -> list[Track]:
        """Filter tracks based on various criteria.

        All criteria are combined with AND logic. Pass None to ignore a criterion.

        Args:
            collection: The Collection to filter.
            genre: Filter by exact genre match (case-insensitive).
            bpm_range: Filter by BPM range (inclusive), e.g., (128, 132).
            key: Filter by musical key (case-insensitive).
            artist: Filter by artist name (case-insensitive substring match).
            min_play_count: Filter by minimum play count.
            date_range: Filter by date added range (inclusive).
            kind: Filter by file type (case-insensitive substring match).

        Returns:
            List of tracks matching all specified criteria.
        """
        results: list[Track] = []

        for track in collection.tracks.values():
            # Genre filter
            if genre is not None and track.genre.lower() != genre.lower():
                continue

            # BPM range filter
            if bpm_range is not None:
                if not (bpm_range[0] <= track.bpm <= bpm_range[1]):
                    continue

            # Key filter
            if key is not None and track.key.lower() != key.lower():
                continue

            # Artist filter (substring match)
            if artist is not None and artist.lower() not in track.artist.lower():
                continue

            # Min play count filter
            if min_play_count is not None and track.play_count < min_play_count:
                continue

            # Date range filter
            if date_range is not None:
                if not (date_range[0] <= track.date_added <= date_range[1]):
                    continue

            # Kind filter (substring match)
            if kind is not None and kind.lower() not in track.kind.lower():
                continue

            results.append(track)

        return results

    @staticmethod
    def search(collection: Collection, query: str) -> list[Track]:
        """Search tracks by name, artist, or album.

        Performs a case-insensitive substring search across name, artist, and album fields.

        Args:
            collection: The Collection to search.
            query: The search query string.

        Returns:
            List of tracks matching the query in any of the searchable fields.
        """
        query_lower = query.lower()
        results: list[Track] = []

        for track in collection.tracks.values():
            if (
                query_lower in track.name.lower()
                or query_lower in track.artist.lower()
                or query_lower in track.album.lower()
            ):
                results.append(track)

        return results

    @staticmethod
    def get_playlist(collection: Collection, name: str) -> list[Track] | None:
        """Get all tracks in a playlist by name.

        Searches recursively through all playlist folders.

        Args:
            collection: The Collection containing the playlist.
            name: The exact playlist name to find.

        Returns:
            List of Track objects in the playlist, or None if not found.
        """
        playlist = collection.playlists.find_playlist(name)
        if playlist is None:
            return None

        return [
            collection.tracks[key]
            for key in playlist.track_keys
            if key in collection.tracks
        ]

    @staticmethod
    def get_playlist_names(collection: Collection) -> list[str]:
        """Get a list of all playlist names (not folders).

        Args:
            collection: The Collection to get playlist names from.

        Returns:
            List of playlist names (folders are excluded).
        """
        return [playlist.name for playlist in collection.playlists.iter_playlists()]

    @staticmethod
    def genre_counts(collection: Collection) -> dict[str, int]:
        """Count tracks by genre.

        Args:
            collection: The Collection to analyze.

        Returns:
            Dictionary mapping genre names to track counts, sorted by count descending.
        """
        counter = Counter(track.genre for track in collection.tracks.values())
        return dict(counter.most_common())

    @staticmethod
    def bpm_distribution(collection: Collection) -> dict[float, int]:
        """Count tracks by BPM.

        Args:
            collection: The Collection to analyze.

        Returns:
            Dictionary mapping BPM values to track counts, sorted by count descending.
        """
        counter = Counter(track.bpm for track in collection.tracks.values())
        return dict(counter.most_common())

    @staticmethod
    def key_distribution(collection: Collection) -> dict[str, int]:
        """Count tracks by musical key.

        Args:
            collection: The Collection to analyze.

        Returns:
            Dictionary mapping key names to track counts, sorted by count descending.
        """
        counter = Counter(track.key for track in collection.tracks.values())
        return dict(counter.most_common())

    @staticmethod
    def artists_by_track_count(collection: Collection) -> list[tuple[str, int]]:
        """Get artists sorted by number of tracks.

        Args:
            collection: The Collection to analyze.

        Returns:
            List of (artist, count) tuples, sorted by count descending.
        """
        counter = Counter(track.artist for track in collection.tracks.values())
        return counter.most_common()


# Convenience functions that wrap the static methods
def filter_tracks(
    collection: Collection,
    *,
    genre: str | None = None,
    bpm_range: tuple[float, float] | None = None,
    key: str | None = None,
    artist: str | None = None,
    min_play_count: int | None = None,
    date_range: tuple[date, date] | None = None,
    kind: str | None = None,
) -> list[Track]:
    """Filter tracks based on various criteria. See CollectionHelpers.filter_tracks."""
    return CollectionHelpers.filter_tracks(
        collection,
        genre=genre,
        bpm_range=bpm_range,
        key=key,
        artist=artist,
        min_play_count=min_play_count,
        date_range=date_range,
        kind=kind,
    )


def search(collection: Collection, query: str) -> list[Track]:
    """Search tracks by name, artist, or album. See CollectionHelpers.search."""
    return CollectionHelpers.search(collection, query)


def get_playlist(collection: Collection, name: str) -> list[Track] | None:
    """Get all tracks in a playlist by name. See CollectionHelpers.get_playlist."""
    return CollectionHelpers.get_playlist(collection, name)


def get_playlist_names(collection: Collection) -> list[str]:
    """Get a list of all playlist names. See CollectionHelpers.get_playlist_names."""
    return CollectionHelpers.get_playlist_names(collection)


def genre_counts(collection: Collection) -> dict[str, int]:
    """Count tracks by genre. See CollectionHelpers.genre_counts."""
    return CollectionHelpers.genre_counts(collection)


def bpm_distribution(collection: Collection) -> dict[float, int]:
    """Count tracks by BPM. See CollectionHelpers.bpm_distribution."""
    return CollectionHelpers.bpm_distribution(collection)


def key_distribution(collection: Collection) -> dict[str, int]:
    """Count tracks by musical key. See CollectionHelpers.key_distribution."""
    return CollectionHelpers.key_distribution(collection)


def artists_by_track_count(collection: Collection) -> list[tuple[str, int]]:
    """Get artists sorted by number of tracks. See CollectionHelpers.artists_by_track_count."""
    return CollectionHelpers.artists_by_track_count(collection)
