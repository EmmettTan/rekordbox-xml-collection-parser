#!/usr/bin/env python3
"""
Example: Find tracks in a playlist filtered by BPM range and key.

Usage:
    python filter_playlist_by_bpm_and_key.py <collection.xml>

    # Using the test fixture:
    python filter_playlist_by_bpm_and_key.py ../tests/fixtures/test_collection.xml

    # Using your own collection (substitute your path):
    python filter_playlist_by_bpm_and_key.py /path/to/your/collection.xml
"""

import sys
from pathlib import Path

from rekordbox_collection_reader import parse_collection, get_playlist, get_playlist_names


def main():
    if len(sys.argv) < 2:
        print("Usage: python filter_playlist_by_bpm_and_key.py <collection.xml>")
        print()
        print("Examples:")
        print("  python filter_playlist_by_bpm_and_key.py ../tests/fixtures/test_collection.xml")
        print("  python filter_playlist_by_bpm_and_key.py /path/to/your/collection.xml")
        sys.exit(1)

    collection_path = Path(sys.argv[1])

    if not collection_path.exists():
        print(f"Error: {collection_path} not found")
        sys.exit(1)

    collection = parse_collection(collection_path)
    print(f"Loaded {len(collection.tracks)} tracks from collection\n")

    # Configuration - customize these values for your collection
    playlist_name = "High Energy"  # Change to your playlist name
    bpm_min = 138.0
    bpm_max = 145.0
    target_key = "Am"  # A minor

    # Get tracks from the playlist
    playlist_tracks = get_playlist(collection, playlist_name)

    if playlist_tracks is None:
        print(f"Playlist '{playlist_name}' not found!")
        print("\nAvailable playlists:")
        for name in get_playlist_names(collection)[:20]:
            print(f"  - {name}")
        return

    print(f"Found {len(playlist_tracks)} tracks in '{playlist_name}'")

    # Filter by BPM range and key
    matching_tracks = [
        track for track in playlist_tracks
        if bpm_min <= track.bpm <= bpm_max and track.key == target_key
    ]

    print(f"Tracks between {bpm_min}-{bpm_max} BPM in {target_key}: {len(matching_tracks)}\n")

    if not matching_tracks:
        print("No matching tracks found.")
        print("\nTry adjusting your filters. Here are some tracks in the playlist:")
        for track in playlist_tracks[:5]:
            print(f"  {track.artist} - {track.name} ({track.bpm} BPM, {track.key})")
        return

    # Display results
    print("-" * 70)
    for track in matching_tracks:
        print(f"{track.artist} - {track.name}")
        print(f"  BPM: {track.bpm}  |  Key: {track.key} ({track.camelot_key})  |  Duration: {track.duration_formatted}")
        print(f"  File: {Path(track.location).name}")
        print()


if __name__ == "__main__":
    main()
