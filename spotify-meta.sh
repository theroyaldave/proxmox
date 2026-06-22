#!/bin/bash
CLIENT_ID="a1b462689527446d9abf037f325b75a3"
CLIENT_SECRET="83ac5a018f8144a0a452ee1558367503"
TRACK_ID="$1"
DEVICE="$2"
META_FILE="/var/www/snapcast-ui/now-playing.json"
FEATURES_FILE="/var/www/snapcast-ui/now-playing-features.json"
[ -z "$TRACK_ID" ] || [ -z "$DEVICE" ] && exit 0

TOKEN=$(curl -s -X POST "https://accounts.spotify.com/api/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
[ -z "$TOKEN" ] && exit 0

curl -s "https://api.spotify.com/v1/tracks/${TRACK_ID}" \
  -H "Authorization: Bearer ${TOKEN}" > /tmp/spotify_track.json

curl -s "https://api.spotify.com/v1/audio-features/${TRACK_ID}" \
  -H "Authorization: Bearer ${TOKEN}" > /tmp/spotify_features.json

python3 /tmp/spotify_meta_parse.py "${DEVICE}" "${META_FILE}" "${FEATURES_FILE}"
