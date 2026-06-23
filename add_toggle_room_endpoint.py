with open("/usr/local/bin/snapcast-api.py", "r") as f:
    c = f.read()

new_endpoint = """
        elif parsed.path == '/hue-toggle-room':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                import ssl, urllib.request as ur
                data = json.loads(body)
                room_id = data.get('room_id', '')
                turn_on = data.get('on', False)
                if not room_id:
                    raise Exception('room_id requis')
                cfg = json.load(open('/var/www/snapcast-ui/hue-config.json'))
                bridge = cfg.get('bridge', '192.168.2.70')
                token = cfg.get('token', '')
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                # Trouver le grouped_light de la room
                req = ur.Request(f'https://{bridge}/clip/v2/resource/room/{room_id}',
                                 headers={'hue-application-key': token})
                room_data = json.loads(ur.urlopen(req, context=ctx, timeout=10).read()).get('data', [{}])[0]
                services = room_data.get('services', [])
                grouped_light_id = next((s['rid'] for s in services if s['rtype'] == 'grouped_light'), None)
                if not grouped_light_id:
                    raise Exception('grouped_light introuvable')

                if turn_on:
                    # Activer scene Lumineux
                    req_scenes = ur.Request(f'https://{bridge}/clip/v2/resource/scene',
                                           headers={'hue-application-key': token})
                    all_scenes = json.loads(ur.urlopen(req_scenes, context=ctx, timeout=10).read()).get('data', [])
                    lumineux = next((s for s in all_scenes
                                    if s.get('group', {}).get('rid') == room_id
                                    and s['metadata']['name'] == 'Lumineux'), None)
                    if lumineux:
                        payload = json.dumps({'recall': {'action': 'active'}}).encode()
                        req2 = ur.Request(f'https://{bridge}/clip/v2/resource/scene/{lumineux["id"]}',
                                         data=payload,
                                         headers={'hue-application-key': token, 'Content-Type': 'application/json'},
                                         method='PUT')
                        ur.urlopen(req2, context=ctx, timeout=10)
                    else:
                        # Fallback: allumer simplement
                        payload = json.dumps({'on': {'on': True}}).encode()
                        req2 = ur.Request(f'https://{bridge}/clip/v2/resource/grouped_light/{grouped_light_id}',
                                         data=payload,
                                         headers={'hue-application-key': token, 'Content-Type': 'application/json'},
                                         method='PUT')
                        ur.urlopen(req2, context=ctx, timeout=10)
                else:
                    # Eteindre
                    payload = json.dumps({'on': {'on': False}}).encode()
                    req2 = ur.Request(f'https://{bridge}/clip/v2/resource/grouped_light/{grouped_light_id}',
                                     data=payload,
                                     headers={'hue-application-key': token, 'Content-Type': 'application/json'},
                                     method='PUT')
                    ur.urlopen(req2, context=ctx, timeout=10)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'on': turn_on}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
"""

marker = "\n        else:\n            self.send_response(404)\n            self.end_headers()\n"
if marker in c:
    c = c.replace(marker, new_endpoint + marker)
    print("hue-toggle-room ajouté")
else:
    print("MARKER NOT FOUND")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(c)

count = c.count("parsed.path == '/hue-toggle-room'")
print(f"hue-toggle-room: {'✓' if count == 1 else '✗ ('+str(count)+'x)'}")
