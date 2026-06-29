#!/usr/bin/env python3
# patch_hue_auto.py

import re

# ── 1. Ajouter endpoint /hue-state dans snapcast-api.py ──────────────────────
content = open('/usr/local/bin/snapcast-api.py').read()

new_endpoint = '''
        elif parsed.path == '/hue-state':
            import os as _os2
            path = '/var/www/snapcast-ui/hue-state.json'
            if self.command == 'POST':
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                try:
                    data = json.loads(body)
                    with open(path, 'w') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'ok'}).encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
            else:
                try:
                    data = json.load(open(path)) if _os2.path.exists(path) else {}
                except:
                    data = {}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())'''

old = "        else:\n            self.send_response(404)\n            self.end_headers()"
new = new_endpoint.strip() + "\n        else:\n            self.send_response(404)\n            self.end_headers()"

if old in content:
    content = content.replace(old, new)
    open('/usr/local/bin/snapcast-api.py', 'w').write(content)
    print('OK: endpoint /hue-state ajouté')
else:
    print('FAILED: anchor not found')

# ── 2. Créer hue-auto-scene.py ───────────────────────────────────────────────
hue_auto = '''#!/usr/bin/env python3
"""
hue-auto-scene.py
Appelé par spotify-meta.sh après chaque changement de piste.
Usage: python3 hue-auto-scene.py <stream_id>
"""
import sys, json, os, ssl, random, urllib.request

BRIDGE = '192.168.2.70'
TOKEN = 'NqTWScJIlAHiwumno8qS8QodlUXYXHttDNsZiO-s'
HUE_CONFIG = '/var/www/snapcast-ui/hue-config.json'
HUE_STATE  = '/var/www/snapcast-ui/hue-state.json'
FEATURES   = '/var/www/snapcast-ui/now-playing-features.json'
STREAM_SCENE_FILE = '/var/www/snapcast-ui/hue-stream-scene.json'

if len(sys.argv) < 2:
    sys.exit(0)

stream_id = sys.argv[1]

def load_json(path, default=None):
    try:
        return json.load(open(path))
    except:
        return default if default is not None else {}

def hue_request(method, endpoint, body=None):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = f'https://{BRIDGE}/clip/v2/resource/{endpoint}'
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
          headers={'hue-application-key': TOKEN, 'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    return json.loads(resp.read())

# Charger les configs
cfg = load_json(HUE_CONFIG)
state = load_json(HUE_STATE)   # {groupId: {active: bool, currentScene: str, lastStyle: str}}
features = load_json(FEATURES)
stream_scenes = load_json(STREAM_SCENE_FILE)  # {streamId: {scene: str, style: str}}

# Style du stream actuel
style_id = (features.get(stream_id) or {}).get('style', 'defaut')

# Récupérer la scène pour ce stream
prev = stream_scenes.get(stream_id, {})
prev_style = prev.get('style', '')
prev_scene = prev.get('scene', '')

def get_scene_for_style(room_name, style_id):
    style = next((s for s in cfg.get('styles', []) if s['id'] == style_id), None)
    if not style:
        return 'Lumineux'
    scenes = style.get('scenes', [])
    valid = [s for s in scenes if s]
    if not valid:
        return 'Lumineux'
    return random.choice(valid)

# Si le style a changé, tirer une nouvelle scène
if style_id != prev_style or not prev_scene:
    scene_name = get_scene_for_style('', style_id)
    stream_scenes[stream_id] = {'scene': scene_name, 'style': style_id}
    with open(STREAM_SCENE_FILE, 'w') as f:
        json.dump(stream_scenes, f)
else:
    scene_name = prev_scene

# Activer la scène sur toutes les rooms actives pour ce stream
changed = False
for group_id, group_state in state.items():
    if not group_state.get('active'):
        continue
    if group_state.get('stream') != stream_id:
        continue
    if group_state.get('lastStyle') == style_id and group_state.get('currentScene') == scene_name:
        continue
    room_id = cfg.get('GROUP_HUE_ROOM', {}).get(group_id)
    if not room_id:
        # Chercher dans la config
        room_name = group_state.get('roomName', '')
        room_cfg = cfg.get('rooms', {}).get(room_name, {})
        room_id = room_cfg.get('hue_room_id', '')
    if not room_id:
        continue
    try:
        # Trouver l'ID de scène sur le bridge
        all_scenes = hue_request('GET', 'scene').get('data', [])
        scene = next((s for s in all_scenes
                      if s.get('group', {}).get('rid') == room_id
                      and s['metadata']['name'] == scene_name), None)
        if scene:
            hue_request('PUT', f'scene/{scene["id"]}/recall', {'action': 'active'})
            state[group_id]['currentScene'] = scene_name
            state[group_id]['lastStyle'] = style_id
            changed = True
    except Exception as e:
        pass

if changed:
    with open(HUE_STATE, 'w') as f:
        json.dump(state, f, indent=2)
'''

with open('/usr/local/bin/hue-auto-scene.py', 'w') as f:
    f.write(hue_auto)
os.chmod('/usr/local/bin/hue-auto-scene.py', 0o755)
print('OK: hue-auto-scene.py créé')
