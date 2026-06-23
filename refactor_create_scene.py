import re

with open("/usr/local/bin/snapcast-api.py", "r") as f:
    c = f.read()

# Remplacer le bloc create-custom-scene complet
old_create = r"""        elif parsed\.path == '/create-custom-scene':.*?self\.wfile\.write\(json\.dumps\(\{'status': 'error', 'message': str\(e\)\}\)\.encode\(\)\)"""

new_create = """        elif parsed.path == '/create-custom-scene':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                scene_name = data.get('name', '').strip()
                colors_hex = data.get('colors', [])
                speed = float(data.get('speed', 0.5))
                image_file = data.get('image_file', '')
                if not scene_name:
                    raise Exception('Nom de scenario requis')
                if not colors_hex:
                    raise Exception('Au moins une couleur requise')

                # Sauvegarder dans custom-scenes.json uniquement
                custom_path = '/var/www/snapcast-ui/custom-scenes.json'
                try:
                    custom = json.load(open(custom_path))
                except:
                    custom = {'scenes': []}

                custom['scenes'] = [s for s in custom['scenes'] if s['name'] != scene_name]
                custom['scenes'].append({
                    'name': scene_name,
                    'colors': colors_hex,
                    'speed': speed,
                    'image_file': image_file,
                    'mode': 'dynamic_palette',
                    'custom': True
                })
                with open(custom_path, 'w') as f:
                    json.dump(custom, f, indent=2, ensure_ascii=False)

                # Mettre à jour known_scenes dans hue-config.json
                cfg = json.load(open('/var/www/snapcast-ui/hue-config.json'))
                known = cfg.get('known_scenes', [])
                known = [s for s in known if s['name'] != scene_name]
                known.append({'name': scene_name, 'colors': colors_hex, 'mode': 'dynamic_palette'})
                cfg['known_scenes'] = known
                with open('/var/www/snapcast-ui/hue-config.json', 'w') as f:
                    json.dump(cfg, f, indent=2, ensure_ascii=False)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'ok',
                    'scene_name': scene_name,
                    'message': 'Scenario sauvegarde localement. Il sera cree sur le bridge au prochain Sauvegarder.'
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())"""

result = re.sub(old_create, new_create, c, flags=re.DOTALL)
if result == c:
    print("REGEX NOT MATCHED - trying manual search")
    # Trouver les positions
    start = c.find("        elif parsed.path == '/create-custom-scene':")
    # Trouver le prochain elif ou else
    next_block = c.find("\n        elif parsed.path == '/delete-custom-scene':", start)
    if start > 0 and next_block > 0:
        c = c[:start] + new_create + "\n" + c[next_block:]
        print(f"Manual replacement: {start} -> {next_block}")
    else:
        print(f"start={start}, next={next_block}")
else:
    c = result
    print("Regex replacement OK")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(c)

# Vérif
print("create-custom-scene bridge calls:", "ur.urlopen" in c[c.find("'/create-custom-scene'"):c.find("'/delete-custom-scene'")])
print("custom only:", "Scenario sauvegarde localement" in c)
