with open("/usr/local/bin/snapcast-api.py", "r") as f:
    c = f.read()

new_endpoint = """
        elif parsed.path == '/push-scene-to-room':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                import ssl, urllib.request as ur
                data = json.loads(body)
                scene_name = data.get('scene_name', '').strip()
                room_id = data.get('room_id', '')
                if not scene_name or not room_id:
                    raise Exception('scene_name et room_id requis')

                cfg = json.load(open('/var/www/snapcast-ui/hue-config.json'))
                bridge = cfg.get('bridge', '192.168.2.70')
                token = cfg.get('token', '')
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                # Charger la scene depuis custom-scenes.json
                custom = json.load(open('/var/www/snapcast-ui/custom-scenes.json'))
                scene_data = next((s for s in custom['scenes'] if s['name'] == scene_name), None)
                if not scene_data:
                    raise Exception(f'Scene "{scene_name}" introuvable dans custom-scenes.json')

                colors_hex = scene_data.get('colors', [])
                speed = float(scene_data.get('speed', 0.5))

                def hex_to_rgb(h):
                    h = h.lstrip('#')
                    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

                def rgb_to_xy(r, g, b):
                    r, g, b = r/255.0, g/255.0, b/255.0
                    r = ((r+0.055)/1.055)**2.4 if r > 0.04045 else r/12.92
                    g = ((g+0.055)/1.055)**2.4 if g > 0.04045 else g/12.92
                    b = ((b+0.055)/1.055)**2.4 if b > 0.04045 else b/12.92
                    X = r*0.664511 + g*0.154324 + b*0.162028
                    Y = r*0.283881 + g*0.668433 + b*0.047685
                    Z = r*0.000088 + g*0.072310 + b*0.986039
                    total = X+Y+Z
                    if total == 0: return {'x': 0.0, 'y': 0.0}
                    return {'x': round(X/total,4), 'y': round(Y/total,4)}

                palette_colors = []
                for hx in colors_hex:
                    try:
                        r,g,b = hex_to_rgb(hx)
                        xy = rgb_to_xy(r,g,b)
                        palette_colors.append({'color': {'xy': xy}, 'dimming': {'brightness': 100.0}})
                    except: pass

                clean_palette = {
                    'color': palette_colors,
                    'dimming': [{'brightness': 100.0}],
                    'color_temperature': []
                }

                # Récupérer les lumières de la room
                req_lights = ur.Request(f'https://{bridge}/clip/v2/resource/light', headers={'hue-application-key': token})
                all_lights = json.loads(ur.urlopen(req_lights, context=ctx, timeout=10).read()).get('data', [])
                req_rooms = ur.Request(f'https://{bridge}/clip/v2/resource/room', headers={'hue-application-key': token})
                all_rooms = json.loads(ur.urlopen(req_rooms, context=ctx, timeout=10).read()).get('data', [])

                room = next((r for r in all_rooms if r['id'] == room_id), None)
                if not room:
                    raise Exception(f'Room {room_id} introuvable')
                device_ids = {c['rid'] for c in room.get('children', []) if c['rtype'] == 'device'}
                light_ids = [l['id'] for l in all_lights if l.get('owner', {}).get('rid') in device_ids]

                if not light_ids:
                    raise Exception('Aucune lumière trouvée dans cette pièce')

                actions = []
                for i, lid in enumerate(light_ids):
                    ce = palette_colors[i % len(palette_colors)] if palette_colors else {'color': {'xy': {'x': 0.3, 'y': 0.3}}, 'dimming': {'brightness': 100.0}}
                    actions.append({'target': {'rid': lid, 'rtype': 'light'}, 'action': {'on': {'on': True}, 'color': ce['color'], 'dimming': ce['dimming']}})

                payload = json.dumps({
                    'metadata': {'name': scene_name},
                    'group': {'rid': room_id, 'rtype': 'room'},
                    'actions': actions,
                    'palette': clean_palette,
                    'speed': speed,
                    'auto_dynamic': True
                }).encode()

                req2 = ur.Request(
                    f'https://{bridge}/clip/v2/resource/scene',
                    data=payload,
                    headers={'hue-application-key': token, 'Content-Type': 'application/json'},
                    method='POST'
                )
                result = json.loads(ur.urlopen(req2, context=ctx, timeout=10).read())
                if not result.get('data'):
                    raise Exception(str(result.get('errors', 'Erreur inconnue')))

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'scene': scene_name}).encode())
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
    print("push-scene-to-room ajouté")
else:
    print("MARKER NOT FOUND")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(c)

count = c.count("parsed.path == '/push-scene-to-room'")
print(f"push-scene-to-room: {'✓' if count == 1 else '✗ ('+str(count)+'x)'}")
