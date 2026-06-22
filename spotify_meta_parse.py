#!/usr/bin/env python3
import json, os, sys, time, urllib.request, urllib.parse

device = sys.argv[1]
meta_file = sys.argv[2]
features_file = sys.argv[3]

CLIENT_ID = "a1b462689527446d9abf037f325b75a3"
CLIENT_SECRET = "83ac5a018f8144a0a452ee1558367503"
TOKENS_FILE = "/var/lib/snapcast-spotify/tokens.json"
LASTFM_KEY = "5ab3bfefc9340a5c95533e696754a004"

# Mapping tags Last.fm → style Hue
TAG_STYLE_MAP = {
    "energique":    ["rock","metal","punk","hard rock","electronic","edm","dance","dubstep","techno","electro","drum and bass","industrial","power metal","thrash metal","progressive rock"],
    "dansant":      ["pop","rnb","r&b","soul","funk","disco","motown","dance pop","synth-pop","new wave","reggaeton","latin","tropical"],
    "festif":       ["hip-hop","hip hop","rap","party","feel good","happy","dancehall","reggae","ska","afrobeat","afropop"],
    "calme":        ["ambient","chill","relax","sleep","downtempo","lo-fi","lofi","new age","meditation","drone","slowcore"],
    "melancolique": ["sad","melancholy","melancholic","depression","post-rock","shoegaze","emo","indie","dark","goth","gothic"],
    "acoustique":   ["jazz","blues","acoustic","folk","country","singer-songwriter","bossa nova","flamenco","world","celtic"],
    "instrumental": ["classical","piano","instrumental","opera","symphony","composer","orchestra","chamber","baroque","renaissance","string"],
    "defaut":       []
}

def tags_to_style(tags):
    tags_lower = [t.lower() for t in tags]
    scores = {style: 0 for style in TAG_STYLE_MAP}
    for style, keywords in TAG_STYLE_MAP.items():
        for kw in keywords:
            for tag in tags_lower:
                if kw in tag:
                    scores[style] += 1
    best = max(scores, key=lambda s: scores[s])
    if scores[best] == 0:
        return "defaut"
    return best

def get_lastfm_tags(artist):
    try:
        artist_enc = urllib.parse.quote(artist)
        url = f"https://ws.audioscrobbler.com/2.0/?method=artist.getTopTags&artist={artist_enc}&api_key={LASTFM_KEY}&format=json"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read())
        tags = [t['name'] for t in data.get('toptags', {}).get('tag', [])]
        return tags[:15]
    except Exception as e:
        print(f"LastFM error: {e}", file=sys.stderr)
        return []

try:
    track = json.load(open('/tmp/spotify_track.json'))

    track_data = {
        'track': track['name'],
        'artist': ', '.join(a['name'] for a in track['artists']),
        'album': track['album']['name'],
        'cover': track['album']['images'][0]['url'] if track['album']['images'] else ''
    }

    # Mettre à jour now-playing.json
    try:
        existing = json.load(open(meta_file)) if os.path.exists(meta_file) else {}
        if not isinstance(existing, dict) or 'track' in existing:
            existing = {}
    except:
        existing = {}
    existing[device] = track_data
    open(meta_file, 'w').write(json.dumps(existing))

    # Récupérer les tags Last.fm et calculer le style
    artist_name = track['artists'][0]['name'] if track['artists'] else ''
    tags = get_lastfm_tags(artist_name)
    style = tags_to_style(tags)

    feat_data = {
        'style': style,
        'tags': tags[:5]
    }

    try:
        existing_f = json.load(open(features_file)) if os.path.exists(features_file) else {}
        if not isinstance(existing_f, dict):
            existing_f = {}
    except:
        existing_f = {}
    existing_f[device] = feat_data
    open(features_file, 'w').write(json.dumps(existing_f))

    print(f"OK: {artist_name} → style={style} tags={tags[:5]}")

except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
