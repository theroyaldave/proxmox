#!/usr/bin/env python3
"""
Patch snapcast-api.py : /activate-hue-scene lit le mode depuis custom-scenes.json
"""

path = '/usr/local/bin/snapcast-api.py'

with open(path, 'r') as f:
    lines = f.readlines()

# Trouver la ligne contenant "Vérifier le mode depuis hue-config.json known_scenes"
target = None
for i, line in enumerate(lines):
    if 'known_scenes' in line and 'known =' in line:
        # Cherche le bloc de 4 lignes : known=, scene_info=, action=
        if i+2 < len(lines) and 'scene_info' in lines[i+1] and 'action' in lines[i+2]:
            target = i
            break

if target is None:
    print('ERROR: bloc cible non trouvé')
    exit(1)

print(f'Bloc trouvé à la ligne {target+1}')
print('Avant:')
for l in lines[target:target+4]:
    print(' ', repr(l))

indent = '                '
new_lines = [
    f'{indent}# Vérifier le mode depuis custom-scenes.json\n',
    f'{indent}known = {{s["name"]: s for s in cfg.get("known_scenes", [])}}\n',
    f'{indent}try:\n',
    f'{indent}    custom_data = json.load(open("/var/www/snapcast-ui/custom-scenes.json"))\n',
    f'{indent}    known.update({{s["name"]: s for s in custom_data.get("scenes", [])}})\n',
    f'{indent}except: pass\n',
    f'{indent}scene_info = known.get(scene_name, {{}})\n',
    f'{indent}action = "dynamic_palette" if scene_info.get("mode") == "dynamic_palette" else "active"\n',
]

lines[target:target+3] = new_lines

with open(path, 'w') as f:
    f.writelines(lines)

print('Patch OK')
print('Après:')
for l in new_lines:
    print(' ', repr(l))
