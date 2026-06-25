#!/usr/bin/env python3
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/opt/mediastack/symlink-watcher.sh'
lines = open(path).read().split('\n')

for i, line in enumerate(lines):
    if 'title=$(echo' in line and '([0-9])' in line:
        print(f"Ligne {i+1} avant : {repr(line)}")
        lines[i] = (
            '        title=$(echo "$relname"'
            ' | sed "s/[.(]*${year}.*//g"'
            " | sed 's/\\([0-9]\\)\\.\\([0-9]\\)/\\1\\2/g'"
            ' | sed "s/[._]/ /g"'
            ' | sed "s/  */ /g"'
            ' | sed "s/^ //;s/ $//")'
        )
        print(f"Ligne {i+1} après  : {repr(lines[i])}")

open(path, 'w').write('\n'.join(lines))
print("Done")
