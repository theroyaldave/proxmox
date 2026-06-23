with open("/usr/local/bin/snapcast-api.py", "r") as f:
    c = f.read()

new_endpoints = """
        elif parsed.path == '/hue-get-room-scenes':
            try:
                import ssl, urllib.request as ur
                from urllib.parse import parse_qs
                params = parse_qs(parsed.query) if parsed.query else {}
                room_id = params.get('room_id', [''])[0]
                cfg = __import__('json').load(open('/var/www/snapcast-ui/hue-config.json'))
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
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())

        elif parsed.path == '/hue-delete-room-scene':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                import ssl, urllib.request as ur
                data = json.loads(body)
                scene_id = data.get('scene_id', '')
                if not scene_id:
                    raise Exception('scene_id requis')
                cfg = json.load(open('/var/www/snapcast-ui/hue-config.json'))
                bridge = cfg.get('bridge', '192.168.2.70')
                token = cfg.get('token', '')
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = ur.Request(
                    f'https://{bridge}/clip/v2/resource/scene/{scene_id}',
                    headers={'hue-application-key': token},
                    method='DELETE'
                )
                ur.urlopen(req, context=ctx, timeout=10)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'deleted': scene_id}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
"""

marker = "\n        else:\n            self.send_response(404)\n            self.end_headers()\n"
if marker in c:
    c = c.replace(marker, new_endpoints + marker)
    print("Endpoints ajoutés")
else:
    print("MARKER NOT FOUND")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(c)

for p in ['/hue-get-room-scenes', '/hue-delete-room-scene']:
    count = c.count(f"parsed.path == '{p}'")
    print(f"  {'✓' if count == 1 else '✗ ('+str(count)+'x)'} {p}")
