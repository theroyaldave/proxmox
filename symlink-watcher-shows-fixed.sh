#!/bin/sh

RADARR_URL="http://radarr:7878"
SONARR_URL="http://sonarr:8989"
SONARR_KEY="0f1cbd43c8f24c22b8163e79ff43e6ce"
RADARR_KEY="18be05bc7daf481fa8000b28c6a46dd5"
SYMLINKS_DIR="/data/symlinks/shows"

get_sonarr_series() {
    title="$1"
    wget -qO- "$SONARR_URL/api/v3/series?apikey=$SONARR_KEY" 2>/dev/null | python3 -c "
import sys, json, re
def norm(s):
    s = re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
    return re.sub(r' +', ' ', s)
def words(s):
    return set(norm(s).split())
series = json.loads(sys.stdin.read())
title = norm('$title')
best = None
best_score = 0
for s in series:
    titles = [s.get('title','')] + [a.get('title','') for a in s.get('alternateTitles', [])]
    for t in titles:
        tw = words(title)
        mw = words(norm(t))
        common = len(tw & mw)
        total = len(tw | mw)
        score = common / total if total > 0 else 0
        if score > best_score and score > 0.35:
            best_score = score
            best = str(s['id']) + '|' + str(s.get('year','')) + '|' + s['path'] + '|' + s['title']
if best:
    print(best)
" 2>/dev/null
}

parse_episode() {
    filename="$1"
    echo "$filename" | python3 -c "
import sys, re
f = sys.stdin.read().strip()
m = re.search(r'[Ss](\d+)[Ee](\d+)', f)
if m:
    print(m.group(1).zfill(2) + '|' + m.group(2).zfill(2))
" 2>/dev/null
}

create_show_symlinks() {
    find /mnt/decypharr/__all__ -mindepth 2 -maxdepth 3 \( -name "*.mkv" -o -name "*.mp4" \) 2>/dev/null | while read filepath; do
        filename=$(basename "$filepath")
        
        # Detect episode pattern S01E01
        ep_info=$(parse_episode "$filename")
        [ -z "$ep_info" ] && continue
        
        season=$(echo "$ep_info" | cut -d'|' -f1)
        episode=$(echo "$ep_info" | cut -d'|' -f2)
        
        # Extract series title from folder name
        relname=$(basename "$(dirname "$filepath")")
        # Remove episode info and beyond
        title=$(echo "$relname" | sed "s/[Ss][0-9][0-9].*//g" | sed "s/[._]/ /g" | sed "s/  */ /g" | sed "s/^ //;s/ $//")
        [ -z "$title" ] && title=$(echo "$filename" | sed "s/[Ss][0-9][0-9][Ee][0-9][0-9].*//g" | sed "s/[._]/ /g" | sed "s/  */ /g" | sed "s/^ //;s/ $//")
        
        result=$(get_sonarr_series "$title")
        if [ -z "$result" ]; then
            echo "No match: $title"
            continue
        fi
        
        series_id=$(echo "$result" | cut -d'|' -f1)
        series_year=$(echo "$result" | cut -d'|' -f2)
        series_path=$(echo "$result" | cut -d'|' -f3)
        series_title=$(echo "$result" | cut -d'|' -f4)
        series_dir=$(basename "$series_path")
        
        season_dir="$SYMLINKS_DIR/$series_dir/Season $((10#$season))"
        destfile="$season_dir/$filename"
        series_root="$SYMLINKS_DIR/$series_dir"

        # FIX DOUBLON: chercher si un lien existant (n'importe ou sous le dossier de la serie)
        # porte deja le meme nom de fichier, peu importe la saison/sous-dossier.
        # Si trouve a un autre endroit que la destination attendue, on le supprime
        # pour eviter d'avoir le meme episode en double (ex: a plat ET dans Season X/).
        if [ -d "$series_root" ]; then
            existing_link=$(find "$series_root" -name "$filename" -type l 2>/dev/null | head -1)
            if [ -n "$existing_link" ] && [ "$existing_link" != "$destfile" ]; then
                echo "Doublon detecte, suppression de l'ancien lien: $existing_link"
                rm -f "$existing_link"
            fi
        fi

        if [ ! -L "$destfile" ]; then
            echo "Creating: $destfile"
            mkdir -p "$season_dir"
            ln -sf "$filepath" "$destfile"
            
            # Save RD mapping
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
            key = 'sonarr_$series_id'
            data[key] = {'hash': t.get('hash',''), 'rd_id': t.get('id') or '', 'filename': fname, 'title': '$series_title'}
            json.dump(data, open(f,'w'), indent=2)
            print(f'Saved mapping: sonarr_$series_id -> {t["id"]}')
            break
except Exception as e:
    print(f'Mapping error: {e}')
" 2>/dev/null
            
            # Notify Sonarr
            wget -qO- --header="Content-Type: application/json" --post-data="{\"name\":\"RescanSeries\",\"seriesId\":$series_id}" "$SONARR_URL/api/v3/command?apikey=$SONARR_KEY" > /dev/null 2>&1
            
            echo "Done: $series_dir S${season}E${episode}"
        fi
    done
}

while true; do
    create_show_symlinks
    sleep 30
done
