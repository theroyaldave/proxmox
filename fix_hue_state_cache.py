import re

with open('/var/www/snapcast-ui/lumieres.html', 'r') as f:
    src = f.read()

# Trouver et remplacer loadRoomLightStates
old = re.search(r'async function loadRoomLightStates\(\) \{.*?await Promise\.all\(promises\);', src, re.DOTALL)
if not old:
    print('RATE - fonction non trouvee')
    exit()

print('Trouve lignes:', src[:old.start()].count('\n')+1, 'a', src[:old.end()].count('\n')+1)

new_fn = """async function loadRoomLightStates() {
  if (!currentConfig || !currentConfig.rooms) return;
  // Charger depuis sessionStorage immediatement (non-bloquant)
  Object.entries(currentConfig.rooms).forEach(function([roomName, roomCfg]) {
    if (!roomCfg.hue_room_id || roomCfg.enabled === false) return;
    try {
      var cached = sessionStorage.getItem('hueState_'+roomName);
      if (cached) {
        var d = JSON.parse(cached);
        currentConfig.rooms[roomName]._lightOn = d._lightOn || false;
        currentConfig.rooms[roomName]._activeScene = d._activeScene || null;
      }
    } catch(e) {}
  });
  // Interroger le bridge en arriere-plan sans bloquer
  Object.entries(currentConfig.rooms).forEach(function([roomName, roomCfg]) {
    if (!roomCfg.hue_room_id || roomCfg.enabled === false) return;
    fetch('/hue-get-state?room_id='+roomCfg.hue_room_id).then(function(r){return r.json();}).then(function(data){
      if (data.light_state) currentConfig.rooms[roomName]._lightOn = data.light_state.on === true;
      if (data.active_scene) currentConfig.rooms[roomName]._activeScene = data.active_scene;
      try {
        sessionStorage.setItem('hueState_'+roomName, JSON.stringify({
          _lightOn: currentConfig.rooms[roomName]._lightOn,
          _activeScene: currentConfig.rooms[roomName]._activeScene
        }));
      } catch(e) {}
      render();
    }).catch(function(){});
  });"""

src = src[:old.start()] + new_fn + src[old.end():]

with open('/var/www/snapcast-ui/lumieres.html', 'w') as f:
    f.write(src)

print('OK - lignes:', len(src.splitlines()))
