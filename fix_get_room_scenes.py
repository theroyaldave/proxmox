import re

with open("/usr/local/bin/snapcast-api.py", "r") as f:
    c = f.read()

# Extraire le bloc hue-get-room-scenes de do_POST
m = re.search(
    r"\n        elif parsed\.path == '/hue-get-room-scenes':.*?(?=\n        elif |\n        else:)",
    c, re.DOTALL
)
if m:
    get_room_scenes_block = m.group()
    print(f"Found block: {len(get_room_scenes_block)} chars")
    # Supprimer de do_POST
    c = c[:m.start()] + c[m.end():]
    print("Removed from do_POST")
else:
    print("Block NOT FOUND in do_POST")
    get_room_scenes_block = """
        elif parsed.path == '/hue-get-room-scenes':
            try:
                import ssl, urllib.request as ur
                from urllib.parse import parse_qs as _pqs
                params = _pqs(parsed.query) if parsed.query else {}
                room_id = params.get('room_id', [''])[0]
                cfg = json.load(open('/var/www/snapcast-ui/hue-config.json'))
                bridge = cfg.get('bridge', '192.168.2.70')
                token = cfg.get('token', '')
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = ur.Request(f'https://{bridge}/clip/v2/resource/scene',
                                 headers={'hue-application-key': token})
                all_scenes = json.loads(ur.urlopen(req, context=ctx, timeout=10).read()).get('data', [])
                room_scenes = [
                    {'id': s['id'], 'name': s['metadata']['name'], 'speed': s.get('speed', 0.5)}
                    for s in all_scenes
                    if s.get('group', {}).get('rid') == room_id
                ]
                room_scenes.sort(key=lambda x: x['name'])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'scenes': room_scenes}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())"""

# Ajouter dans do_GET avant le else final
get_marker = "\n        else:\n            self.send_response(404)\n            self.end_headers()\n\nHTTPServer"
if get_marker in c:
    c = c.replace(get_marker, get_room_scenes_block + get_marker)
    print("Added to do_GET")
else:
    # Chercher la fin de do_GET
    get_marker2 = "        else:\n            self.send_response(404)\n            self.end_headers()\n\nHTTPServer"
    if get_marker2 in c:
        c = c.replace(get_marker2, get_room_scenes_block.lstrip('\n') + "\n        " + get_marker2)
        print("Added to do_GET (variant)")
    else:
        print("do_GET marker NOT FOUND")
        # Montrer la fin du fichier
        print(repr(c[-300:]))

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(c)

# Vérifier positions
post_pos = c.find("def do_POST")
get_pos = c.find("def do_GET(")
scene_pos = c.find("'/hue-get-room-scenes'")
print(f"do_POST at: {post_pos}")
print(f"do_GET at: {get_pos}")
print(f"hue-get-room-scenes at: {scene_pos}")
print(f"In do_GET: {scene_pos > get_pos}")
