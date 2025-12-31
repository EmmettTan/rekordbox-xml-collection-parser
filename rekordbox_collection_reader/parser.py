"""XML parser for rekordbox collection files."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import unquote

from .models import Collection, PlaylistNode, PositionMark, Tempo, Track


def parse_collection(xml_path: str | Path) -> Collection:
    """Parse a rekordbox XML export file into a Collection object.

    Args:
        xml_path: Path to the rekordbox XML export file.

    Returns:
        A Collection object containing all tracks and playlists.

    Raises:
        FileNotFoundError: If the XML file does not exist.
        ET.ParseError: If the XML is malformed.
    """
    xml_path = Path(xml_path)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Parse product info
    product_elem = root.find("PRODUCT")
    product_name = product_elem.get("Name", "rekordbox") if product_elem is not None else "rekordbox"
    product_version = product_elem.get("Version", "") if product_elem is not None else ""

    # Parse tracks
    tracks: dict[int, Track] = {}
    collection_elem = root.find("COLLECTION")
    if collection_elem is not None:
        for track_elem in collection_elem.findall("TRACK"):
            track = _parse_track(track_elem)
            tracks[track.track_id] = track

    # Parse playlists
    playlists_elem = root.find("PLAYLISTS")
    if playlists_elem is not None:
        root_node = playlists_elem.find("NODE")
        playlists = _parse_playlist_node(root_node) if root_node is not None else PlaylistNode(name="ROOT", node_type=0)
    else:
        playlists = PlaylistNode(name="ROOT", node_type=0)

    return Collection(
        product_name=product_name,
        product_version=product_version,
        tracks=tracks,
        playlists=playlists,
    )


def _parse_track(elem: ET.Element) -> Track:
    """Parse a TRACK element into a Track object."""
    # Parse tempos
    tempos = [_parse_tempo(t) for t in elem.findall("TEMPO")]

    # Parse cue points
    cue_points = [_parse_position_mark(p) for p in elem.findall("POSITION_MARK")]

    # Parse location and URL-decode it
    location_raw = elem.get("Location", "")
    # Remove file://localhost prefix and URL-decode
    location = _decode_location(location_raw)

    # Parse date
    date_str = elem.get("DateAdded", "")
    date_added = date.fromisoformat(date_str) if date_str else date.today()

    return Track(
        track_id=int(elem.get("TrackID", "0")),
        name=elem.get("Name", ""),
        artist=elem.get("Artist", ""),
        album=elem.get("Album", ""),
        genre=elem.get("Genre", ""),
        bpm=float(elem.get("AverageBpm", "0")),
        key=elem.get("Tonality", ""),
        duration=int(elem.get("TotalTime", "0")),
        location=location,
        date_added=date_added,
        play_count=int(elem.get("PlayCount", "0")),
        rating=int(elem.get("Rating", "0")),
        kind=elem.get("Kind", ""),
        size=int(elem.get("Size", "0")),
        bit_rate=int(elem.get("BitRate", "0")),
        sample_rate=int(elem.get("SampleRate", "0")),
        comments=elem.get("Comments", ""),
        label=elem.get("Label", ""),
        remixer=elem.get("Remixer", ""),
        composer=elem.get("Composer", ""),
        grouping=elem.get("Grouping", ""),
        mix=elem.get("Mix", ""),
        year=int(elem.get("Year", "0")),
        disc_number=int(elem.get("DiscNumber", "0")),
        track_number=int(elem.get("TrackNumber", "0")),
        tempos=tempos,
        cue_points=cue_points,
    )


def _parse_tempo(elem: ET.Element) -> Tempo:
    """Parse a TEMPO element into a Tempo object."""
    return Tempo(
        inizio=float(elem.get("Inizio", "0")),
        bpm=float(elem.get("Bpm", "0")),
        metro=elem.get("Metro", "4/4"),
        battito=int(elem.get("Battito", "1")),
    )


def _parse_position_mark(elem: ET.Element) -> PositionMark:
    """Parse a POSITION_MARK element into a PositionMark object."""
    red = elem.get("Red")
    green = elem.get("Green")
    blue = elem.get("Blue")

    return PositionMark(
        name=elem.get("Name", ""),
        type=int(elem.get("Type", "0")),
        start=float(elem.get("Start", "0")),
        num=int(elem.get("Num", "-1")),
        red=int(red) if red is not None else None,
        green=int(green) if green is not None else None,
        blue=int(blue) if blue is not None else None,
    )


def _parse_playlist_node(elem: ET.Element) -> PlaylistNode:
    """Parse a NODE element into a PlaylistNode object (recursive)."""
    node_type = int(elem.get("Type", "0"))
    name = elem.get("Name", "")

    if node_type == 1:  # Playlist
        # Get track keys
        track_keys = [int(t.get("Key", "0")) for t in elem.findall("TRACK")]
        return PlaylistNode(
            name=name,
            node_type=node_type,
            track_keys=track_keys,
        )
    else:  # Folder
        # Recursively parse children
        children = [_parse_playlist_node(child) for child in elem.findall("NODE")]
        return PlaylistNode(
            name=name,
            node_type=node_type,
            children=children,
        )


def _decode_location(location: str) -> str:
    """Decode a rekordbox file location URL to a file path.

    Args:
        location: A URL-encoded file path, typically starting with
                  "file://localhost/".

    Returns:
        A decoded file path string.
    """
    # Remove file://localhost prefix
    if location.startswith("file://localhost"):
        location = location[16:]  # len("file://localhost") == 16

    # URL-decode the path
    return unquote(location)
