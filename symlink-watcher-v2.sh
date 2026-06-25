#!/bin/sh

RADARR_URL="http://radarr:7878"
RADARR_KEY="18be05bc7daf481fa8000b28c6a46dd5"
SYMLINKS_DIR="/data/symlinks/movies"

get_radarr_movie() {
    title="$1"
    year="$2"
    wget -qO- "$RADARR_URL/api/v3/movie?apikey=$RADARR_KEY" 2>/dev/null | python3 -c "
import sys, json, re
def norm(s):
    s = re.sub(r'(\d)\.(\d)', r'\1\2', s)
    s = re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
    return re.sub(r' +', ' ', s)
def words(s):
    return set(norm(s).split())
def score(t1, t2):
    w1, w2 = words(t1), words(t2)
    common = len(w1 & w2)
    total = len(w1 | w2)
    return common / total if total > 0 else 0
movies = json.loads(sys.stdin.read())
title = norm('$title')
year = '$year'
best = None
best_score = 0
for m in movies:
    y = str(m.get('year',''))
    if y != year:
        continue
    titles = [m.get('title',''), m.get('originalTitle','')]
    for alt in m.get('alternateTitles', []):
        titles.append(alt.get('title',''))
    for t in titles:
        s = score(title, norm(t))
        if s > best_score and s > 0.35:
            best_score = s
            best = str(m['id']) + ' ' + m['path']
if best:
    print(best)
" 2>/dev/null
}

clear_radarr_queue() {
    movie_id="$1"
    queue_ids=$(wget -qO- "$RADARR_URL/api/v3/queue?apikey=$RADARR_KEY&movieId=$movie_id" 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for r in data.get('records', []):
    if r.get('movieId') == $movie_id:
        print(r['id'])
" 2>/dev/null)
    for qid in $queue_ids; do
        wget -qO- --method=DELETE "$RADARR_URL/api/v3/queue/$qid?apikey=$RADARR_KEY&removeFromClient=true&blocklist=false" > /dev/null 2>&1
        echo "Cleared queue ID $qid for movie $movie_id"
    done
}

mark_downloaded() {
    movie_id="$1"
    filename="$2"
    now=$(date -u +"%Y-%m-%d %H:%M:%S.0000000Z")
    existing=$(sqlite3 /radarr-config/radarr.db "SELECT Id FROM MovieFiles WHERE MovieId=$movie_id;" 2>/dev/null)
    if [ -z "$existing" ]; then
        quality='{"quality":16,"revision":{"version":1,"real":0,"isRepack":false}}'
        file_id=$(sqlite3 /radarr-config/radarr.db "INSERT INTO MovieFiles (MovieId, Quality, Size, DateAdded, RelativePath, Languages, IndexerFlags, OriginalFilePath) VALUES ($movie_id, '$quality', 1, '$now', '$filename', '[2,1]', 0, 'radarr/$filename'); SELECT last_insert_rowid();" 2>/dev/null)
        sqlite3 /radarr-config/radarr.db "UPDATE Movies SET MovieFileId=$file_id WHERE Id=$movie_id;" 2>/dev/null
        echo "Marked as downloaded in Radarr DB for movie ID $movie_id (file ID $file_id)"
    fi
}

create_symlinks() {
    find /mnt/decypharr/__all__ -mindepth 2 -maxdepth 2 -name "*.mkv" -o -name "*.mp4" 2>/dev/null | while read filepath; do
        filename=$(basename "$filepath")
        relname=$(basename "$(dirname "$filepath")")
        year=$(echo "$relname" | grep -oE "(19|20)[0-9]{2}" | head -1)
        [ -z "$year" ] && continue
        echo "$relname" | grep -qiE "S[0-9]{2}E?[0-9]{0,2}" && continue
        title=$(echo "$relname" | python3 -c "
import sys, re
s = sys.stdin.read().strip()
year = '$year'
s = re.sub(r'[.(]*' + year + r'.*', '', s)
s = re.sub(r'(\d)\.(\d)', r'\1\2', s)
s = re.sub(r'[._]', ' ', s)
s = re.sub(r' +', ' ', s).strip()
print(s)
")
        result=$(get_radarr_movie "$title" "$year")
        if [ -z "$result" ]; then
            echo "No match: $title ($year)"
            continue
        fi
        movie_id=$(echo "$result" | cut -d" " -f1)
        movie_path=$(echo "$result" | cut -d" " -f2-)
        movie_dir=$(basename "$movie_path")
        destfile="$SYMLINKS_DIR/$movie_dir/$filename"
        if [ ! -L "$destfile" ]; then
            echo "Creating: $destfile"
            mkdir -p "$SYMLINKS_DIR/$movie_dir"
            ln -sf "$filepath" "$destfile"
            python3 -c "
import json, os, re, urllib.request
try:
    RD_KEY = 'AGWMLUEMYM7NPZ5PKNL7IO3KVRHWK65GIZ5U5FOJQIPAQJWFN5FA'
    url = f'https://api.real-debrid.com/rest/1.0/torrents?auth_token={RD_KEY}&limit=100'
    torrents = json.loads(urllib.request.urlopen(url).read())
    fname = '$filename'
    def norm(s):
        return re.sub(r'[^a-z0-9]', ' ', s.lower()).strip()
    for t in torrents:
        if norm(t.get('filename',''))[:20] == norm(fname)[:20]:
            f = '/data/symlinks/rd-mapping.json'
            data = json.load(open(f)) if os.path.exists(f) else {}
            data['$movie_id'] = {'hash': t.get('hash',''), 'rd_id': t['id'] if 'id' in t else '', 'filename': fname, 'title': '$movie_dir'}
            json.dump(data, open(f,'w'), indent=2)
            print('Saved mapping: $movie_id -> ' + str(t.get('id','')))
            break
except Exception as e:
    print(f'Mapping error: {e}')
" 2>/dev/null
            rd_hash=$(wget -qO- "http://decypharr:8282/api/v1/queue" 2>/dev/null | python3 -c "
import sys, json, re
try:
    data = json.loads(sys.stdin.read())
    for item in data if isinstance(data, list) else data.get('records', []):
        name = item.get('name','') or item.get('title','')
        if '$relname' in name or name in '$relname':
            print(item.get('hash',''))
            break
except: pass
" 2>/dev/null)
            if [ -n "$rd_hash" ]; then
                python3 -c "
import json, os
f = '/data/symlinks/rd-mapping.json'
data = json.load(open(f)) if os.path.exists(f) else {}
data['$movie_id'] = {'hash': '$rd_hash', 'filename': '$filename', 'title': '$movie_dir'}
json.dump(data, open(f,'w'))
" 2>/dev/null
                echo "Saved RD hash for movie $movie_id: $rd_hash"
            fi
            mark_downloaded "$movie_id" "$filename"
            echo "Done: $movie_dir"
        fi
        clear_radarr_queue "$movie_id"
    done
}

while true; do
    create_symlinks
    sleep 30
done
