#!/usr/bin/env python3
import json, os, sys, time, urllib.request, urllib.parse

device = sys.argv[1]
meta_file = sys.argv[2]
features_file = sys.argv[3]

CLIENT_ID = "a1b462689527446d9abf037f325b75a3"
CLIENT_SECRET = "83ac5a018f8144a0a452ee1558367503"
TOKENS_FILE = "/var/lib/snapcast-spotify/tokens.json"

def get_oauth_token():
    try:
        tokens = json.load(open(TOKENS_FILE))
        if time.time() < tokens.get('expires_at', 0) - 60:
            return tokens['access_token']
        # Refresh
        if 'refresh_token' not in tokens:
            return None
        data = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }).encode()
        req = urllib.request.Request('https://accounts.spotify.com/api/token', data=data)
        resp = urllib.request.urlopen(req, timeout=10)
        new_tokens = json.loads(resp.read())
        tokens['access_token'] = new_tokens['access_token']
        tokens['expires_at'] = time.time() + new_tokens.get('expires_in', 3600)
        json.dump(tokens, open(TOKENS_FILE, 'w'))
        return tokens['access_token']
    except Exception as e:
        print(f"Token error: {e}", file=sys.stderr)
        return None

try:
    track = json.load(open('/tmp/spotify_track.json'))

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

    # Audio features via OAuth token
    track_id = track['id']
    oauth_token = get_oauth_token()
    feat_data = {}
    if oauth_token:
        try:
            req = urllib.request.Request(
                f'https://api.spotify.com/v1/audio-features/{track_id}',
                headers={'Authorization': f'Bearer {oauth_token}'}
            )
            resp = urllib.request.urlopen(req, timeout=10)
            features = json.loads(resp.read())
            feat_data = {
                'energy':           features.get('energy', 0),
                'danceability':     features.get('danceability', 0),
                'valence':          features.get('valence', 0),
                'acousticness':     features.get('acousticness', 0),
                'instrumentalness': features.get('instrumentalness', 0)
            }
        except Exception as e:
            print(f"Features error: {e}", file=sys.stderr)

    try:
        existing_f = json.load(open(features_file)) if os.path.exists(features_file) else {}
        if not isinstance(existing_f, dict):
            existing_f = {}
    except:
        existing_f = {}
    existing_f[device] = feat_data
    open(features_file, 'w').write(json.dumps(existing_f))

except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
