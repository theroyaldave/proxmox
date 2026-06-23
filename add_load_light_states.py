with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# Ajouter la fonction loadRoomLightStates et l'appeler après loadCustomScenes
load_states_fn = """
async function loadRoomLightStates() {
  if (!currentConfig || !currentConfig.rooms) return;
  var promises = Object.entries(currentConfig.rooms).map(async function([roomName, roomCfg]) {
    if (!roomCfg.hue_room_id || roomCfg.enabled === false) return;
    try {
      var r = await fetch('/hue-get-state?room_id='+roomCfg.hue_room_id);
      var data = await r.json();
      if (data.light_state) {
        currentConfig.rooms[roomName]._lightOn = data.light_state.on === true;
      }
    } catch(e) {}
  });
  await Promise.all(promises);
}
"""

c = c.replace(
    "// \u2500\u2500\u2500 APERCU AMPOULES",
    load_states_fn + "\n// \u2500\u2500\u2500 APERCU AMPOULES"
)

# Appeler loadRoomLightStates après loadCustomScenes et avant render
c = c.replace(
    "    await loadCustomScenes();\n    render();",
    "    await loadCustomScenes();\n    await loadRoomLightStates();\n    render();"
)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("loadRoomLightStates:", "loadRoomLightStates" in c)
print("await loadRoomLightStates:", "await loadRoomLightStates" in c)
