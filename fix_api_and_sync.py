import re

with open("/usr/local/bin/snapcast-api.py", "r") as f:
    content = f.read()

# ─── 1. Supprimer les blocs dupliqués ───
# Les doublons sont : activate-hue-scene (383), hue-get-state (1054),
# upload-scene-image (1093), create-custom-scene (1137), delete-custom-scene (1235)
# Stratégie : pour chaque elif dupliqué, garder la PREMIÈRE occurrence, supprimer les suivantes

def remove_duplicate_elif(text, path):
    """Supprime les occurrences dupliquées d'un elif parsed.path == 'path'"""
    pattern = r"(\n        elif parsed\.path == '" + re.escape(path) + r"':.*?)(?=\n        elif |\n        else:)"
    matches = list(re.finditer(pattern, text, re.DOTALL))
    if len(matches) <= 1:
        print(f"  {path}: {len(matches)} occurrence(s) - OK")
        return text
    print(f"  {path}: {len(matches)} occurrences - suppression des doublons")
    # Garder la première, supprimer les autres
    for m in reversed(matches[1:]):
        text = text[:m.start()] + text[m.end():]
    return text

print("Nettoyage des doublons...")
for path in ['/activate-hue-scene', '/hue-get-state', '/upload-scene-image',
             '/create-custom-scene', '/delete-custom-scene']:
    content = remove_duplicate_elif(content, path)

# ─── 2. Ajouter /hue-sync-scenes avant le else final de do_POST ───
sync_endpoint = """
        elif parsed.path == '/hue-sync-scenes':
            try:
                import ssl, urllib.request as ur
                cfg = json.load(open('/var/www/snapcast-ui/hue-config.json'))
                bridge = cfg.get('bridge', '192.168.2.70')
                token = cfg.get('token', '')
                source_room_id = cfg.get('source_room_id', '')
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                def xy_to_hex(x, y):
                    # CIE xy + Y=1 -> RGB
                    z = 1.0 - x - y
                    if y == 0: return '#ffffff'
                    Y = 1.0
                    X = (Y / y) * x
                    Z = (Y / y) * z
                    # Wide RGB D65 inverse
                    r =  X * 1.656492 - Y * 0.354851 - Z * 0.255038
                    g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152
                    b =  X * 0.051713 - Y * 0.121364 + Z * 1.011530
                    # Gamma
                    def gc(v):
                        v = max(0, v)
                        if v <= 0.0031308: return 12.92 * v
                        return 1.055 * (v ** (1/2.4)) - 0.055
                    r, g, b = gc(r), gc(g), gc(b)
                    # Normalize
                    m = max(r, g, b, 1.0)
                    r, g, b = r/m, g/m, b/m
                    return '#{:02x}{:02x}{:02x}'.format(
                        max(0, min(255, int(r*255))),
                        max(0, min(255, int(g*255))),
                        max(0, min(255, int(b*255)))
                    )

                # Récupérer toutes les scènes du bridge
                req = ur.Request(f'https://{bridge}/clip/v2/resource/scene',
                                 headers={'hue-application-key': token})
                all_scenes = json.loads(ur.urlopen(req, context=ctx, timeout=10).read()).get('data', [])

                # Filtrer les scènes de la room source
                source_scenes = [s for s in all_scenes
                                 if s.get('group', {}).get('rid') == source_room_id]

                # Charger custom-scenes.json existant
                custom_path = '/var/www/snapcast-ui/custom-scenes.json'
                try:
                    custom = json.load(open(custom_path))
                except:
                    custom = {'scenes': []}

                # Index des scènes custom existantes
                existing = {s['name']: s for s in custom.get('scenes', [])}

                synced = []
                for s in source_scenes:
                    name = s.get('metadata', {}).get('name', '')
                    if not name:
                        continue
                    speed = s.get('speed', 0.5)
                    mode = 'dynamic_palette' if s.get('auto_dynamic') else 'fixed'
                    # Extraire couleurs depuis palette
                    palette_colors = s.get('palette', {}).get('color', [])
                    colors = []
                    for pc in palette_colors:
                        xy = pc.get('color', {}).get('xy', {})
                        x, y = xy.get('x', 0), xy.get('y', 0)
                        colors.append(xy_to_hex(x, y))
                    # Garder image si déjà dans custom
                    image_file = existing.get(name, {}).get('image_file', '')
                    existing[name] = {
                        'name': name,
                        'colors': colors,
                        'speed': round(speed, 3),
                        'mode': mode,
                        'image_file': image_file,
                        'hue_id': s.get('id', '')
                    }
                    synced.append(name)

                custom['scenes'] = list(existing.values())
                with open(custom_path, 'w') as f:
                    json.dump(custom, f, indent=2, ensure_ascii=False)

                # Mettre à jour known_scenes dans hue-config.json
                cfg['known_scenes'] = [
                    {'name': sc['name'], 'colors': sc['colors'], 'mode': sc['mode']}
                    for sc in custom['scenes']
                ]
                with open('/var/www/snapcast-ui/hue-config.json', 'w') as f:
                    json.dump(cfg, f, indent=2, ensure_ascii=False)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'ok',
                    'synced': len(synced),
                    'scenes': synced
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
"""

# Insérer avant le else final de do_POST
marker = "\n        else:\n            self.send_response(404)\n            self.end_headers()\n"
if marker in content:
    content = content.replace(marker, sync_endpoint + marker)
    print("hue-sync-scenes ajouté")
else:
    print("MARKER NOT FOUND")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(content)

# Vérifications
paths = ['/activate-hue-scene', '/hue-get-state', '/upload-scene-image',
         '/create-custom-scene', '/delete-custom-scene', '/hue-sync-scenes']
for p in paths:
    count = content.count(f"parsed.path == '{p}'")
    status = "✓" if count == 1 else f"✗ ({count}x)"
    print(f"  {status} {p}")

# Valider syntaxe Python
import py_compile, tempfile, os
tmp = tempfile.mktemp(suffix='.py')
with open(tmp, 'w') as f:
    f.write(content)
try:
    py_compile.compile(tmp, doraise=True)
    print("SYNTAXE PYTHON OK")
except py_compile.PyCompileError as e:
    print(f"SYNTAX ERROR: {e}")
os.unlink(tmp)
