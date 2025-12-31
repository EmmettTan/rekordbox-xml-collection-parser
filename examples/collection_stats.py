#!/usr/bin/env python3
"""
Example: Display collection statistics.

Usage:
    python collection_stats.py <collection.xml>

    # Using the test fixture:
    python collection_stats.py ../tests/fixtures/test_collection.xml

    # Using your own collection (substitute your path):
    python collection_stats.py /path/to/your/collection.xml
"""

import sys
from pathlib import Path

from rekordbox_collection_reader import (
    parse_collection,
    genre_counts,
    bpm_distribution,
    key_distribution,
    artists_by_track_count,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python collection_stats.py <collection.xml>")
        print()
        print("Examples:")
        print("  python collection_stats.py ../tests/fixtures/test_collection.xml")
        print("  python collection_stats.py /path/to/your/collection.xml")
        sys.exit(1)

    collection_path = Path(sys.argv[1])

    if not collection_path.exists():
        print(f"Error: {collection_path} not found")
        sys.exit(1)

    collection = parse_collection(collection_path)

    print(f"Collection: {collection.product_name} {collection.product_version}")
    print(f"Total tracks: {len(collection.tracks)}")
    print()

    # Top genres
    print("Top 10 Genres:")
    print("-" * 30)
    genres = genre_counts(collection)
    for genre, count in list(genres.items())[:10]:
        bar = "#" * min(count, 50)  # Cap bar length
        print(f"{genre:25} {count:4}  {bar}")
    print()

    # BPM distribution
    print("BPM Distribution (top 10):")
    print("-" * 30)
    bpms = bpm_distribution(collection)
    for bpm, count in list(bpms.items())[:10]:
        bar = "#" * min(count, 50)
        print(f"{bpm:6.0f} BPM  {count:4}  {bar}")
    print()

    # Key distribution
    print("Key Distribution (top 10):")
    print("-" * 30)
    keys = key_distribution(collection)
    for key, count in list(keys.items())[:10]:
        bar = "#" * min(count, 50)
        print(f"{key:6}  {count:4}  {bar}")
    print()

    # Top artists
    print("Top 10 Artists:")
    print("-" * 30)
    artists = artists_by_track_count(collection)
    for artist, count in artists[:10]:
        print(f"{artist:30} {count:3} tracks")


if __name__ == "__main__":
    main()
