#!/usr/bin/env python3
import sys, os

path = sys.argv[1] if len(sys.argv) > 1 else '/opt/mediastack/symlink-watcher.sh'
content = open(path).read()
original = content

# Afficher la ligne title pour debug
for i, line in enumerate(content.split('\n'), 1):
    if 'title=$(echo' in line:
        print(f"Ligne {i}: {repr(line)}")

# Fix 1: sed bash - remplacer //g par /\1\2/g dans l'extraction du titre
# On trouve la ligne et on la remplace entièrement
lines = content.split('\n')
new_lines = []
for line in lines:
    if 'title=$(echo' in line and 'sed' in line and '([0-9])' in line:
        # Reconstruire la ligne correctement
        line = '        title=$(echo "$relname" | sed "s/[.(]*${year}.*//g" | sed \'s/\\([0-9]\\)\\.\\([0-9]\\)/\\1\\2/g\' | sed "s/[._]/ /g" | sed "s/  */ /g" | sed "s/^ //;s/ $//")'
        print(f"Ligne remplacée: {repr(line)}")
    new_lines.append(line)
content = '\n'.join(new_lines)

if content != original:
    open(path, 'w').write(content)
    print('✅ Patch appliqué')
else:
    print('❌ Aucun changement')
