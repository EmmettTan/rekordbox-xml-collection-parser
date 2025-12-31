"""Pydantic models for rekordbox XML data structures."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Iterator


# Camelot key mapping for key conversion
CAMELOT_KEYS: dict[str, str] = {
    # Minor keys
    "Abm": "1A", "Ebm": "2A", "Bbm": "3A", "Fm": "4A",
    "Cm": "5A", "Gm": "6A", "Dm": "7A", "Am": "8A",
    "Em": "9A", "Bm": "10A", "F#m": "11A", "Dbm": "12A",
    # Major keys
    "B": "1B", "F#": "2B", "Db": "3B", "Ab": "4B",
    "Eb": "5B", "Bb": "6B", "F": "7B", "C": "8B",
    "G": "9B", "D": "10B", "A": "11B", "E": "12B",
    # Alternative notations
    "G#m": "1A", "D#m": "2A", "A#m": "3A",
    "C#m": "12A", "Gb": "2B", "C#": "3B", "G#": "4B",
    "D#": "5B", "A#": "6B",
}


class Tempo(BaseModel):
    """Tempo/BPM grid information for a track."""

    inizio: float = Field(description="Start position in seconds")
    bpm: float = Field(description="Beats per minute")
    metro: str = Field(default="4/4", description="Time signature")
    battito: int = Field(default=1, description="Beat number")


class PositionMark(BaseModel):
    """Cue point or memory cue marker."""

    name: str = Field(default="", description="Cue point name/label")
    type: int = Field(default=0, description="Marker type (0=cue, 1=fade-in, 2=fade-out, 3=load, 4=loop)")
    start: float = Field(description="Position in seconds")
    num: int = Field(description="Hot cue number (0-7) or -1 for memory cue")
    red: int | None = Field(default=None, description="Red color component (0-255)")
    green: int | None = Field(default=None, description="Green color component (0-255)")
    blue: int | None = Field(default=None, description="Blue color component (0-255)")

    @property
    def is_hot_cue(self) -> bool:
        """Return True if this is a hot cue (numbered 0-7)."""
        return self.num >= 0

    @property
    def is_memory_cue(self) -> bool:
        """Return True if this is a memory cue (num == -1)."""
        return self.num == -1

    @property
    def color_hex(self) -> str | None:
        """Return the color as a hex string, or None if no color set."""
        if self.red is not None and self.green is not None and self.blue is not None:
            return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"
        return None


class Track(BaseModel):
    """A track in the rekordbox collection."""

    track_id: int = Field(description="Unique track identifier")
    name: str = Field(description="Track title")
    artist: str = Field(default="", description="Artist name")
    album: str = Field(default="", description="Album name")
    genre: str = Field(default="", description="Genre")
    bpm: float = Field(default=0.0, description="Average BPM")
    key: str = Field(default="", description="Musical key (tonality)")
    duration: int = Field(default=0, description="Track length in seconds")
    location: str = Field(description="File path (URL-decoded)")
    date_added: date = Field(description="Date track was added to collection")
    play_count: int = Field(default=0, description="Number of times played")
    rating: int = Field(default=0, description="Rating (0-255, where 255 = 5 stars)")
    kind: str = Field(default="", description="File format (e.g., 'WAV File', 'MP3 File')")
    size: int = Field(default=0, description="File size in bytes")
    bit_rate: int = Field(default=0, description="Bit rate in kbps")
    sample_rate: int = Field(default=0, description="Sample rate in Hz")
    comments: str = Field(default="", description="User comments")
    label: str = Field(default="", description="Record label")
    remixer: str = Field(default="", description="Remixer name")
    composer: str = Field(default="", description="Composer name")
    grouping: str = Field(default="", description="Grouping tag")
    mix: str = Field(default="", description="Mix name")
    year: int = Field(default=0, description="Release year")
    disc_number: int = Field(default=0, description="Disc number")
    track_number: int = Field(default=0, description="Track number on disc")
    tempos: list[Tempo] = Field(default_factory=list, description="Tempo grid information")
    cue_points: list[PositionMark] = Field(default_factory=list, description="Cue points and memory cues")

    @property
    def hot_cues(self) -> list[PositionMark]:
        """Return only hot cues (numbered 0-7)."""
        return [cue for cue in self.cue_points if cue.is_hot_cue]

    @property
    def memory_cues(self) -> list[PositionMark]:
        """Return only memory cues (num == -1)."""
        return [cue for cue in self.cue_points if cue.is_memory_cue]

    @property
    def camelot_key(self) -> str:
        """Convert the musical key to Camelot notation."""
        return CAMELOT_KEYS.get(self.key, "")

    @property
    def duration_formatted(self) -> str:
        """Return duration as MM:SS format."""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def star_rating(self) -> int:
        """Return rating as 0-5 stars."""
        if self.rating == 0:
            return 0
        # rekordbox uses 51, 102, 153, 204, 255 for 1-5 stars
        return min(5, (self.rating + 50) // 51)


class PlaylistNode(BaseModel):
    """A playlist or folder node in the playlist tree."""

    name: str = Field(description="Playlist or folder name")
    node_type: int = Field(description="0 = folder, 1 = playlist")
    track_keys: list[int] = Field(default_factory=list, description="Track IDs (for playlists)")
    children: list[PlaylistNode] = Field(default_factory=list, description="Child nodes (for folders)")

    @property
    def is_folder(self) -> bool:
        """Return True if this node is a folder."""
        return self.node_type == 0

    @property
    def is_playlist(self) -> bool:
        """Return True if this node is a playlist."""
        return self.node_type == 1

    def iter_playlists(self) -> Iterator[PlaylistNode]:
        """Recursively iterate through all playlists in this node and its children."""
        if self.is_playlist:
            yield self
        for child in self.children:
            yield from child.iter_playlists()

    def find_playlist(self, name: str) -> PlaylistNode | None:
        """Find a playlist by name (searches recursively)."""
        if self.is_playlist and self.name == name:
            return self
        for child in self.children:
            result = child.find_playlist(name)
            if result is not None:
                return result
        return None


class Collection(BaseModel):
    """The complete rekordbox collection."""

    product_name: str = Field(default="rekordbox", description="Product name")
    product_version: str = Field(default="", description="Product version")
    tracks: dict[int, Track] = Field(default_factory=dict, description="Tracks keyed by TrackID")
    playlists: PlaylistNode = Field(description="Root playlist node")
