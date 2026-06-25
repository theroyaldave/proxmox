#!/usr/bin/env python3
"""
Patch symlink-watcher.sh :
- Supprime SequenceMatcher (faux positifs)
- Ajoute normalisation 2.0 -> 20
- Filtre séries TV (S01, S02...)
- clear_radarr_queue appelée même si symlink existe déjà
"""

import re

SCRIPT_PATH = '/symlink-watcher.sh'

content = open(SCRIPT_PATH).read()
original = content

# 1. Normalisation chiffre.chiffre dans la fonction norm Python
old = '''def norm(s):
    s = re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
    return re.sub(r' +', ' ', s)'''
new = '''def norm(s):
    s = re.sub(r'(\\d)\\.(\\d)', r'\\1\\2', s)
    s = re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
    return re.sub(r' +', ' ', s)'''
content = content.replace(old, new)

# 2. Supprimer SequenceMatcher, garder uniquement Jaccard
old = '''    from difflib import SequenceMatcher
    seq = SequenceMatcher(None, norm(t1), norm(t2)).ratio()
    return max(jaccard, seq)'''
new = '''    return jaccard'''
content = content.replace(old, new)

# 3. Normalisation chiffre.chiffre dans l'extraction bash du titre
old = 'sed "s/[.(]*${year}.*//g" | sed "s/[._]/ /g"'
new = 'sed "s/[.(]*${year}.*//g" | sed "s/\\([0-9]\\)\\.\\([0-9]\\)/\\1\\2/g" | sed "s/[._]/ /g"'
content = content.replace(old, new)

# 4. Filtre séries TV
old = '        [ -z "$year" ] && continue\n        title='
new = '        [ -z "$year" ] && continue\n        echo "$relname" | grep -qiE "S[0-9]{2}E?[0-9]{0,2}" && continue\n        title='
content = content.replace(old, new)

# 5. clear_radarr_queue hors du bloc if symlink
old = '        fi\n    done\n}\n\nwhile true;'
new = '        fi\n        clear_radarr_queue "$movie_id"\n    done\n}\n\nwhile true;'
content = content.replace(old, new)

# Vérification
if content == original:
    print('ATTENTION: aucun patch appliqué !')
else:
    open(SCRIPT_PATH, 'w').write(content)
    print('Patch appliqué avec succès')

# Rapport
checks = [
    ('Normalisation 2.0->20 Python', r"re\.sub\(r'\(\\d\)\\\.\\(\\d\)'"),
    ('Jaccard only', 'return jaccard'),
    ('Filtre séries TV', 'grep -qiE'),
    ('Normalisation bash', r'sed "s/\\\([0-9]\\\)\\\.\\\([0-9]\\\)/\\\1\\\2/g"'),
    ('clear_radarr_queue hors if', 'fi\n        clear_radarr_queue'),
]
for label, pattern in checks:
    found = bool(re.search(pattern, content)) if pattern.startswith('r"') or '\\' in pattern else pattern in content
    print(f"  {'✅' if found else '❌'} {label}")
