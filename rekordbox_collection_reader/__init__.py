"""Rekordbox Collection Reader - Parse rekordbox XML exports into Python objects."""

from .helpers import (
    artists_by_track_count,
    bpm_distribution,
    filter_tracks,
    genre_counts,
    get_playlist,
    get_playlist_names,
    key_distribution,
    search,
)
from .models import (
    CAMELOT_KEYS,
    Collection,
    PlaylistNode,
    PositionMark,
    Tempo,
    Track,
)
from .parser import parse_collection

__version__ = "0.1.0"

__all__ = [
    # Main entry point
    "parse_collection",
    # Models
    "Collection",
    "Track",
    "Tempo",
    "PositionMark",
    "PlaylistNode",
    # Constants
    "CAMELOT_KEYS",
    # Helper functions
    "filter_tracks",
    "search",
    "get_playlist",
    "get_playlist_names",
    "genre_counts",
    "bpm_distribution",
    "key_distribution",
    "artists_by_track_count",
]
