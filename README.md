# Rekordbox Collection Reader

A Python library for parsing rekordbox XML collection exports into structured data for analysis, filtering, and querying.

## Features

- Parse rekordbox XML exports into Pydantic models
- Access track metadata: BPM, key, genre, cue points, play count, ratings, and more
- Filter tracks by genre, BPM range, key, artist, date range
- Search across track names, artists, and albums
- Navigate playlist/folder hierarchy
- Get collection statistics (genre counts, BPM distribution, key distribution)
- Camelot key notation support

## Installation

```bash
git clone git@github.com:EmmettTan/rekordbox-xml-collection-parser.git
cd rekordbox-xml-collection-parser
pip install -e .
```

## Quick Start

```python
from rekordbox_collection_reader import parse_collection, filter_tracks, search, get_playlist

# Load your collection (export from rekordbox: File > Export Collection in xml format)
collection = parse_collection("/path/to/your/collection.xml")

print(f"Total tracks: {len(collection.tracks)}")

# Access a track by ID
track = collection.tracks[12345]
print(f"{track.artist} - {track.name}")
print(f"  BPM: {track.bpm}, Key: {track.key} ({track.camelot_key})")
print(f"  Hot cues: {len(track.hot_cues)}, Memory cues: {len(track.memory_cues)}")

# Filter tracks
techno_140s = filter_tracks(
    collection,
    genre="Techno",
    bpm_range=(138, 142),
    key="Am"
)

# Search
results = search(collection, "deadmau5")

# Get tracks from a playlist
playlist_tracks = get_playlist(collection, "My Playlist")
```

## API Reference

### Parsing

```python
from rekordbox_collection_reader import parse_collection

collection = parse_collection("collection.xml")
```

### Models

- `Collection` - The root object containing all tracks and playlists
- `Track` - A track with all metadata, tempo info, and cue points
- `Tempo` - BPM grid information
- `PositionMark` - Hot cue or memory cue
- `PlaylistNode` - A playlist or folder in the playlist tree

### Track Properties

```python
track.name           # Track title
track.artist         # Artist name
track.bpm            # Average BPM
track.key            # Musical key (e.g., "Gm", "F#m")
track.camelot_key    # Camelot notation (e.g., "6A", "11A")
track.genre          # Genre
track.duration       # Length in seconds
track.duration_formatted  # "MM:SS" format
track.play_count     # Play count
track.rating         # Rating (0-255)
track.star_rating    # Rating as 0-5 stars
track.hot_cues       # List of hot cues (numbered 0-7)
track.memory_cues    # List of memory cues
track.location       # File path
track.date_added     # Date added to collection
```

### Helper Functions

```python
from rekordbox_collection_reader import (
    filter_tracks,
    search,
    get_playlist,
    get_playlist_names,
    genre_counts,
    bpm_distribution,
    key_distribution,
    artists_by_track_count,
)

# Filter with multiple criteria
tracks = filter_tracks(
    collection,
    genre="Techno",           # Exact genre match
    bpm_range=(128, 132),     # BPM range (inclusive)
    key="Gm",                 # Musical key
    artist="Charlotte",       # Artist substring match
    min_play_count=5,         # Minimum plays
)

# Search by name, artist, or album
results = search(collection, "query")

# Playlist operations
tracks = get_playlist(collection, "Playlist Name")
names = get_playlist_names(collection)

# Statistics
genre_counts(collection)      # {"Techno": 500, "House": 200, ...}
bpm_distribution(collection)  # {128.0: 150, 130.0: 120, ...}
key_distribution(collection)  # {"Gm": 100, "Am": 95, ...}
artists_by_track_count(collection)  # [("Artist", 50), ...]
```

## Examples

See the [`examples/`](examples/) folder for complete working scripts:

- `filter_playlist_by_bpm_and_key.py` - Find tracks matching BPM/key criteria
- `collection_stats.py` - Display collection statistics
- `find_tracks_missing_cues.py` - Find tracks without hot cues

```bash
cd examples
python collection_stats.py /path/to/your/collection.xml
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
