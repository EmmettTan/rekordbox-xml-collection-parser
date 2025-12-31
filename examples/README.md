# Examples

Example scripts demonstrating how to use the rekordbox-collection-reader library.

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running Examples

All examples require a path to a rekordbox XML collection file:

```bash
cd examples

# Using the included test fixture
python <script>.py ../tests/fixtures/test_collection.xml

# Using your own collection (export from rekordbox: File > Export Collection in xml format)
python <script>.py /path/to/your/collection.xml
```

## Available Examples

### filter_playlist_by_bpm_and_key.py

Find tracks in a specific playlist that match a BPM range and musical key.

```bash
python filter_playlist_by_bpm_and_key.py ../tests/fixtures/test_collection.xml
```

Output:
```
Loaded 15 tracks from collection

Found 4 tracks in 'High Energy'
Tracks between 138.0-145.0 BPM in Am: 1

----------------------------------------------------------------------
Charlotte de Witte - Doppler (Original Mix)
  BPM: 140.0  |  Key: Am (8A)  |  Duration: 5:56
  File: Charlotte_de_Witte_Doppler.mp3
```

### collection_stats.py

Display collection statistics including genre distribution, BPM ranges, key distribution, and top artists.

```bash
python collection_stats.py ../tests/fixtures/test_collection.xml
```

Output:
```
Collection: rekordbox 6.8.5
Total tracks: 15

Top 10 Genres:
------------------------------
Techno                       5  #####
Progressive House            2  ##
Trance                       2  ##
...
```

### find_tracks_missing_cues.py

Find tracks in a playlist that are missing hot cues (useful for identifying tracks that need cue points set).

```bash
python find_tracks_missing_cues.py ../tests/fixtures/test_collection.xml
```

Output:
```
Playlist: Techno Tracks
Total tracks: 6
With hot cues: 4
Missing hot cues: 2

Tracks missing hot cues:
------------------------------------------------------------
Adam Beyer - Your Mind (Original Mix) (3 memory cues)
Pan-Pot - Confronted (Original Mix) (no cues)
```

## Customizing

Each script has configuration variables near the top of `main()` that you can modify:

- `playlist_name` - The playlist to analyze
- `bpm_min` / `bpm_max` - BPM range filter
- `target_key` - Musical key filter (e.g., "Am", "F#m", "Bb")

Edit these values to match your collection and use case.
