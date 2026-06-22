#!/usr/bin/env python3
# patch_save_hue_config.py

import re

content = open('/usr/local/bin/snapcast-api.py').read()

new_endpoint = '''
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

                # Récupérer toutes les scènes existantes sur le bridge
                req = ur.Request(f'https://{bridge}/clip/v2/resource/scene', headers={'hue-application-key': token})
                resp = ur.urlopen(req, context=ctx, timeout=10)
                all_scenes = json.loads(resp.read()).get('data', [])

                # Récupérer toutes les lumières du bridge
                req_lights = ur.Request(f'https://{bridge}/clip/v2/resource/light', headers={'hue-application-key': token})
                resp_lights = ur.urlopen(req_lights, context=ctx, timeout=10)
                all_lights = json.loads(resp_lights.read()).get('data', [])

                # Récupérer toutes les rooms pour avoir les devices
                req_rooms = ur.Request(f'https://{bridge}/clip/v2/resource/room', headers={'hue-application-key': token})
                resp_rooms = ur.urlopen(req_rooms, context=ctx, timeout=10)
                all_rooms = json.loads(resp_rooms.read()).get('data', [])

                def get_room_light_ids(room_id):
                    """Retourne les IDs de lumières d'une room"""
                    room = next((r for r in all_rooms if r['id'] == room_id), None)
                    if not room:
                        return []
                    device_ids = {c['rid'] for c in room.get('children', []) if c['rtype'] == 'device'}
                    return [l['id'] for l in all_lights if l.get('owner', {}).get('rid') in device_ids]

                # Scènes de la room source
                source_scenes = {s['metadata']['name']: s for s in all_scenes
                                 if s.get('group', {}).get('rid') == source_room_id}

                created = []
                errors = []

                for room_name, room_cfg in data.get('rooms', {}).items():
                    if not room_cfg.get('enabled', True):
                        continue
                    room_id = room_cfg.get('hue_room_id', '')
                    if not room_id or room_id == source_room_id:
                        continue

                    # Scènes déjà présentes dans cette pièce
                    room_scenes = {s['metadata']['name'] for s in all_scenes
                                   if s.get('group', {}).get('rid') == room_id}

                    # Lumières de la pièce cible (récupérées en temps réel)
                    target_light_ids = get_room_light_ids(room_id)
                    if not target_light_ids:
                        errors.append(f'{room_name}: aucune lumière trouvée')
                        continue

                    # Collecter tous les noms de scènes nécessaires
                    needed_scenes = set()
                    for style in data.get('styles', []):
                        style_scenes = room_cfg.get('scenes', {}).get(style['id'], style.get('scenes', []))
                        for sname in style_scenes:
                            if sname:
                                needed_scenes.add(sname)

                    # Créer les scènes manquantes
                    for sname in needed_scenes:
                        if sname in room_scenes:
                            continue
                        if sname not in source_scenes:
                            errors.append(f'{room_name}: {sname} - non trouvée dans la source')
                            continue

                        src = source_scenes[sname]

                        # Construire les actions avec les lumières de la pièce cible
                        # On répartit les couleurs de la palette sur les lumières disponibles
                        palette = src.get('palette', {})
                        palette_colors = palette.get('color', [])
                        actions = []
                        for i, light_id in enumerate(target_light_ids):
                            action = {'on': {'on': True}, 'dimming': {'brightness': 80}}
                            if palette_colors:
                                color_entry = palette_colors[i % len(palette_colors)]
                                action['color'] = color_entry.get('color', {})
                                if 'dimming' in color_entry:
                                    action['dimming'] = color_entry['dimming']
                            actions.append({
                                'target': {'rid': light_id, 'rtype': 'light'},
                                'action': action
                            })

                        payload = json.dumps({
                            'metadata': {'name': sname},
                            'group': {'rid': room_id, 'rtype': 'room'},
                            'actions': actions,
                            'palette': palette,
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

# Trouver et remplacer l'ancien save-hue-config
pattern = r"        elif parsed\.path == '/save-hue-config':.*?(?=\n        elif |\n        else:)"
matches = list(re.finditer(pattern, content, re.DOTALL))
print(f"Found {len(matches)} save-hue-config occurrences")

if matches:
    content = content[:matches[0].start()] + new_endpoint.strip() + content[matches[0].end():]
    open('/usr/local/bin/snapcast-api.py', 'w').write(content)
    print('OK' if 'get_room_light_ids' in content else 'FAILED')
else:
    print('FAILED - anchor not found')
