with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS
css = """
.room-active-scene{font-size:10px;color:#444;margin-left:8px;font-style:italic;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:120px;flex-shrink:0}
"""
c = c.replace("</style>", css + "\n</style>")

# 2. Dans loadRoomLightStates, stocker aussi active_scene
old_light_state = """      if (data.light_state) {
        currentConfig.rooms[roomName]._lightOn = data.light_state.on === true;
      }"""

new_light_state = """      if (data.light_state) {
        currentConfig.rooms[roomName]._lightOn = data.light_state.on === true;
      }
      if (data.active_scene !== undefined) {
        currentConfig.rooms[roomName]._activeScene = data.active_scene;
      }"""

if old_light_state in c:
    c = c.replace(old_light_state, new_light_state)
    print("loadRoomLightStates updated OK")
else:
    print("loadRoomLightStates NOT FOUND")

# 3. Dans render(), afficher le scénario actif dans le header
old_header_name = """          <span class="room-name">${roomName}</span>
          ${activateHtml}"""

new_header_name = """          <span class="room-name">${roomName}</span>
          ${roomCfg._activeScene ? `<span class="room-active-scene">${roomCfg._activeScene}</span>` : ''}
          ${activateHtml}"""

if old_header_name in c:
    c = c.replace(old_header_name, new_header_name)
    print("Header active scene OK")
else:
    print("Header NOT FOUND")

# 4. Mettre à jour _activeScene quand on active un scénario
old_activate = """      currentConfig.rooms[roomName]._lightOn = true;
      render();
      showToast('Scene "'+sceneName+'" activée dans '+roomName);"""

new_activate = """      currentConfig.rooms[roomName]._lightOn = true;
      currentConfig.rooms[roomName]._activeScene = sceneName;
      render();
      showToast('"'+sceneName+'" activée dans '+roomName);"""

if old_activate in c:
    c = c.replace(old_activate, new_activate)
    print("activate scene state OK")
else:
    print("activate scene state NOT FOUND")

# 5. Mettre à jour _activeScene quand on éteint
old_off = """      currentConfig.rooms[roomName]._lightOn = turnOn;
      render();
      showToast(turnOn ? roomName+' : allumée' : roomName+' : éteinte');"""

new_off = """      currentConfig.rooms[roomName]._lightOn = turnOn;
      if (!turnOn) currentConfig.rooms[roomName]._activeScene = null;
      else currentConfig.rooms[roomName]._activeScene = 'Lumineux';
      render();
      showToast(turnOn ? roomName+' : allumée' : roomName+' : éteinte');"""

if old_off in c:
    c = c.replace(old_off, new_off)
    print("toggle off state OK")
else:
    print("toggle off NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("room-active-scene CSS:", "room-active-scene" in c)
print("_activeScene:", "_activeScene" in c)
