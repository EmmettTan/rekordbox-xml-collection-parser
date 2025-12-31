#!/usr/bin/env python3
"""
Example: Find tracks that are missing hot cues.

Usage:
    python find_tracks_missing_cues.py <collection.xml>

    # Using the test fixture:
    python find_tracks_missing_cues.py ../tests/fixtures/test_collection.xml

    # Using your own collection (substitute your path):
    python find_tracks_missing_cues.py /path/to/your/collection.xml
"""

import sys
from pathlib import Path

from rekordbox_collection_reader import parse_collection, get_playlist, get_playlist_names


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_tracks_missing_cues.py <collection.xml>")
        print()
        print("Examples:")
        print("  python find_tracks_missing_cues.py ../tests/fixtures/test_collection.xml")
        print("  python find_tracks_missing_cues.py /path/to/your/collection.xml")
        sys.exit(1)

    collection_path = Path(sys.argv[1])

    if not collection_path.exists():
        print(f"Error: {collection_path} not found")
        sys.exit(1)

    collection = parse_collection(collection_path)

    # Change this to your playlist name
    playlist_name = "Techno Tracks"

    tracks = get_playlist(collection, playlist_name)

    if tracks is None:
        print(f"Playlist '{playlist_name}' not found!")
        print("\nAvailable playlists:")
        for name in get_playlist_names(collection)[:15]:
            print(f"  - {name}")
        return

    # Find tracks without hot cues
    missing_cues = [t for t in tracks if len(t.hot_cues) == 0]
    has_cues = [t for t in tracks if len(t.hot_cues) > 0]

    print(f"Playlist: {playlist_name}")
    print(f"Total tracks: {len(tracks)}")
    print(f"With hot cues: {len(has_cues)}")
    print(f"Missing hot cues: {len(missing_cues)}")
    print()

    if missing_cues:
        print("Tracks missing hot cues:")
        print("-" * 60)
        for track in missing_cues:
            mem_cues = len(track.memory_cues)
            cue_info = f"({mem_cues} memory cue{'s' if mem_cues != 1 else ''})" if mem_cues else "(no cues)"
            print(f"{track.artist} - {track.name} {cue_info}")


if __name__ == "__main__":
    main()
