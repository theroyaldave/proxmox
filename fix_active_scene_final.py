import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. Supprimer TOUTES les occurrences de _activeScene dans le header render
c = re.sub(
    r"\s*\$\{isEnabled && roomCfg\._activeScene \? `<span class=\\\"room-active-scene\\\">.*?</span>` : ''\}",
    "",
    c
)
print("Removed header activeScene:", c.count("room-active-scene") <= 2)

# 2. Supprimer TOUTES les occurrences de _activeScene = sceneName en doublon
# Garder seulement celle dans activateSceneInRoom
occurrences = [(m.start(), m.group()) for m in re.finditer(r'currentConfig\.rooms\[roomName\]\._activeScene = sceneName;', c)]
print(f"_activeScene = sceneName occurrences: {len(occurrences)}")

# Garder seulement la première (dans activateSceneInRoom)
if len(occurrences) > 1:
    # Supprimer toutes sauf la première
    for start, match in reversed(occurrences[1:]):
        c = c[:start] + c[start+len(match):]
    print("Duplicates removed")

# 3. Ajouter l'affichage dans le header UNE SEULE FOIS
old_toggle = "          ${isEnabled ? `<button class=\"room-toggle${roomLightOn?' on':''}\" onclick=\"event.stopPropagation();toggleRoomLight('${roomName}','${hueRoomId}',${roomLightOn})\""

new_toggle = "          ${isEnabled && roomCfg._activeScene ? `<span class=\"room-active-scene\">${roomCfg._activeScene}</span>` : ''}\n          ${isEnabled ? `<button class=\"room-toggle${roomLightOn?' on':''}\" onclick=\"event.stopPropagation();toggleRoomLight('${roomName}','${hueRoomId}',${roomLightOn})\""

if old_toggle in c:
    c = c.replace(old_toggle, new_toggle, 1)
    print("Header activeScene added OK")
else:
    print("Toggle NOT FOUND")

# 4. Stocker dans sessionStorage quand on active via 🏠
old_activate_room = "      currentConfig.rooms[roomName]._lightOn = true;\n      currentConfig.rooms[roomName]._activeScene = sceneName;"
new_activate_room = "      currentConfig.rooms[roomName]._lightOn = true;\n      currentConfig.rooms[roomName]._activeScene = sceneName;\n      try { sessionStorage.setItem('activeScene_'+roomName, sceneName); } catch(e) {}"

if old_activate_room in c:
    c = c.replace(old_activate_room, new_activate_room)
    print("sessionStorage set OK")
else:
    print("activate room NOT FOUND")

# 5. Restaurer depuis sessionStorage dans loadRoomLightStates
old_restore = "      // Toujours utiliser l'etat reel du bridge\n      currentConfig.rooms[roomName]._activeScene = data.active_scene || null;"
new_restore = """      // Etat bridge en priorité, sinon sessionStorage
      if (data.active_scene) {
        currentConfig.rooms[roomName]._activeScene = data.active_scene;
        try { sessionStorage.setItem('activeScene_'+roomName, data.active_scene); } catch(e) {}
      } else {
        try {
          var stored = sessionStorage.getItem('activeScene_'+roomName);
          currentConfig.rooms[roomName]._activeScene = stored || null;
        } catch(e) { currentConfig.rooms[roomName]._activeScene = null; }
      }"""

if old_restore in c:
    c = c.replace(old_restore, new_restore)
    print("Restore from sessionStorage OK")
else:
    print("Restore NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("Final _activeScene count:", c.count("_activeScene = sceneName"))
print("sessionStorage:", "sessionStorage" in c)
