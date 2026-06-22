#!/usr/bin/env python3
import json, os, sys

device = sys.argv[1]
meta_file = sys.argv[2]
features_file = sys.argv[3]

try:
    track = json.load(open('/tmp/spotify_track.json'))
    features = json.load(open('/tmp/spotify_features.json'))

    track_data = {
        'track': track['name'],
        'artist': ', '.join(a['name'] for a in track['artists']),
        'album': track['album']['name'],
        'cover': track['album']['images'][0]['url'] if track['album']['images'] else ''
    }

    try:
        existing = json.load(open(meta_file)) if os.path.exists(meta_file) else {}
        if not isinstance(existing, dict) or 'track' in existing:
            existing = {}
    except:
        existing = {}
    existing[device] = track_data
    open(meta_file, 'w').write(json.dumps(existing))

    feat_data = {
        'energy':           features.get('energy', 0),
        'danceability':     features.get('danceability', 0),
        'valence':          features.get('valence', 0),
        'acousticness':     features.get('acousticness', 0),
        'instrumentalness': features.get('instrumentalness', 0)
    }
    try:
        existing_f = json.load(open(features_file)) if os.path.exists(features_file) else {}
        if not isinstance(existing_f, dict):
            existing_f = {}
    except:
        existing_f = {}
    existing_f[device] = feat_data
    open(features_file, 'w').write(json.dumps(existing_f))

except Exception as e:
    import sys
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
