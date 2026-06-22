import re

content = open('/usr/local/bin/snapcast-api.py').read()

hue_endpoint = '''
        elif parsed.path == '/save-hue-config':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                import ssl, urllib.request as ur
                data = json.loads(body)
                bridge = data.get('bridge', '192.168.2.70')
                token = data.get('token', '')
                source_room_id = data.get('source_room_id', '')

                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                # Recuperer toutes les scenes existantes sur le bridge
                req = ur.Request(
                    f'https://{bridge}/clip/v2/resource/scene',
                    headers={'hue-application-key': token}
                )
                resp = ur.urlopen(req, context=ctx, timeout=10)
                all_scenes = json.loads(resp.read()).get('data', [])

                # Recuperer les scenes de la room source (Atelier)
                source_scenes = {s['metadata']['name']: s for s in all_scenes
                                 if s.get('group', {}).get('rid') == source_room_id}

                created = []
                errors = []

                # Pour chaque piece
                for room_name, room_cfg in data.get('rooms', {}).items():
                    if not room_cfg.get('enabled', True):
                        continue
                    room_id = room_cfg.get('hue_room_id', '')
                    if not room_id:
                        continue

                    # Scenes de cette piece
                    room_scenes = {s['metadata']['name']: s for s in all_scenes
                                   if s.get('group', {}).get('rid') == room_id}

                    # Collecter tous les noms de scenes utilises dans cette piece
                    needed_scenes = set()
                    for style in data.get('styles', []):
                        style_scenes = room_cfg.get('scenes', {}).get(style['id'], style.get('scenes', []))
                        for sname in style_scenes:
                            if sname:
                                needed_scenes.add(sname)

                    # Creer les scenes manquantes en copiant depuis la source
                    for sname in needed_scenes:
                        if sname not in room_scenes:
                            if sname in source_scenes:
                                src = source_scenes[sname]
                                payload = json.dumps({
                                    'metadata': {'name': sname},
                                    'group': {'rid': room_id, 'rtype': 'room'},
                                    'actions': src.get('actions', []),
                                    'palette': src.get('palette', {}),
                                    'speed': src.get('speed', 0.6),
                                    'auto_dynamic': src.get('auto_dynamic', True)
                                }).encode()
                                req2 = ur.Request(
                                    f'https://{bridge}/clip/v2/resource/scene',
                                    data=payload,
                                    headers={'hue-application-key': token, 'Content-Type': 'application/json'},
                                    method='POST'
                                )
                                try:
                                    resp2 = ur.urlopen(req2, context=ctx, timeout=10)
                                    result = json.loads(resp2.read())
                                    if result.get('data'):
                                        created.append(f'{room_name}: {sname}')
                                    else:
                                        errors.append(f'{room_name}: {sname} - {result.get("errors")}')
                                except Exception as e2:
                                    errors.append(f'{room_name}: {sname} - {str(e2)}')

                # Sauvegarder hue-config.json
                with open('/var/www/snapcast-ui/hue-config.json', 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'ok',
                    'created': created,
                    'errors': errors
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
'''

# Insérer avant le else final du do_POST
content = content.replace(
    "        else:\n            self.send_response(404)\n            self.end_headers()\n\n    def do_GET",
    hue_endpoint + "        else:\n            self.send_response(404)\n            self.end_headers()\n\n    def do_GET"
)

open('/usr/local/bin/snapcast-api.py', 'w').write(content)
print('OK' if 'save-hue-config' in content else 'FAILED')
