import re

with open("/usr/local/bin/snapcast-api.py", "r") as f:
    c = f.read()

# 1. Dans /create-custom-scene - lire brightness
old_create = """                scene_name = data.get('name', '').strip()
                colors_hex = data.get('colors', [])
                speed = float(data.get('speed', 0.5))
                image_file = data.get('image_file', '')"""

new_create = """                scene_name = data.get('name', '').strip()
                colors_hex = data.get('colors', [])
                speed = float(data.get('speed', 0.5))
                brightness = float(min(100, max(1, data.get('brightness', 100))))
                image_file = data.get('image_file', '')"""

if old_create in c:
    c = c.replace(old_create, new_create)
    print("create-custom-scene brightness read OK")
else:
    print("create NOT FOUND")

# 2. Stocker brightness dans custom-scenes.json
old_store = """                custom['scenes'].append({
                    'name': scene_name,
                    'colors': colors_hex,
                    'speed': speed,
                    'image_file': image_file,
                    'mode': 'dynamic_palette',
                    'custom': True
                })"""

new_store = """                custom['scenes'].append({
                    'name': scene_name,
                    'colors': colors_hex,
                    'speed': speed,
                    'brightness': brightness,
                    'image_file': image_file,
                    'mode': 'dynamic_palette',
                    'custom': True
                })"""

if old_store in c:
    c = c.replace(old_store, new_store)
    print("custom-scenes.json brightness store OK")
else:
    print("store NOT FOUND")

# 3. Dans /push-scene-to-room - utiliser brightness depuis custom-scenes.json
old_push_speed = """                colors_hex = scene_data.get('colors', [])
                speed = float(scene_data.get('speed', 0.5))"""

new_push_speed = """                colors_hex = scene_data.get('colors', [])
                speed = float(scene_data.get('speed', 0.5))
                brightness = float(min(100, max(1, scene_data.get('brightness', 100))))"""

if old_push_speed in c:
    c = c.replace(old_push_speed, new_push_speed)
    print("push-scene-to-room brightness read OK")
else:
    print("push speed NOT FOUND")

# 4. Utiliser brightness dans les actions de push-scene-to-room
old_actions = """                actions.append({'target': {'rid': lid, 'rtype': 'light'}, 'action': {'on': {'on': True}, 'color': ce['color'], 'dimming': ce['dimming']}})"""

new_actions = """                actions.append({'target': {'rid': lid, 'rtype': 'light'}, 'action': {'on': {'on': True}, 'color': ce['color'], 'dimming': {'brightness': brightness}}})"""

if old_actions in c:
    c = c.replace(old_actions, new_actions)
    print("push actions brightness OK")
else:
    print("push actions NOT FOUND")

# 5. Utiliser brightness dans la palette de push-scene-to-room
old_palette_colors = """                    palette_colors.append({'color': {'xy': xy}, 'dimming': {'brightness': 100.0}})"""

new_palette_colors = """                    palette_colors.append({'color': {'xy': xy}, 'dimming': {'brightness': brightness}})"""

# Remplacer seulement dans push-scene-to-room (2e occurrence)
parts = c.split("elif parsed.path == '/push-scene-to-room':")
if len(parts) == 2:
    parts[1] = parts[1].replace(
        "palette_colors.append({'color': {'xy': xy}, 'dimming': {'brightness': 100.0}})",
        "palette_colors.append({'color': {'xy': xy}, 'dimming': {'brightness': brightness}})",
        1
    )
    c = "elif parsed.path == '/push-scene-to-room':".join(parts)
    print("push palette brightness OK")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(c)

import py_compile
try:
    py_compile.compile("/usr/local/bin/snapcast-api.py", doraise=True)
    print("SYNTAX OK")
except py_compile.PyCompileError as e:
    print(f"SYNTAX ERROR: {e}")
