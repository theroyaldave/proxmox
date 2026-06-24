with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# CSS
css = """
.scene-room-dropdown-item.not-present{color:#555}
.scene-room-dropdown-item.not-present:hover{background:#1a1a1a;color:#f5a623}
.scene-room-badge{font-size:9px;margin-left:auto;padding:1px 5px;border-radius:4px;flex-shrink:0}
.scene-room-badge.ok{background:rgba(29,90,69,.3);color:#5dcaa5}
.scene-room-badge.missing{background:rgba(90,60,0,.3);color:#f5a623}
"""
c = c.replace("</style>", css + "\n</style>")

# Modifier toggleSceneRoomMenu pour vérifier roomScenesCache
old_rooms_map = """    + rooms.map(function([rn, rc]) {
        return '<div class="scene-room-dropdown-item" onclick="activateSceneInRoom(event,\\''+rn+'\\',\\''+rc.hue_room_id+'\\',\\''+sceneName.replace(/'/g,"\\\\'")+'\\')">'
          +'<span>'+rn+'</span>'
          +'</div>';
      }).join('');"""

new_rooms_map = """    + rooms.map(function([rn, rc]) {
        var roomScenes = roomScenesCache[rn] || [];
        var hasScene = roomScenes.some(function(s){ return s.name === sceneName; });
        var badge = hasScene
          ? '<span class="scene-room-badge ok">✓</span>'
          : '<span class="scene-room-badge missing">➕</span>';
        var cls = hasScene ? 'scene-room-dropdown-item' : 'scene-room-dropdown-item not-present';
        var title = hasScene ? '' : ' title="Scène absente du bridge — cliquez pour ajouter puis activer"';
        return '<div class="'+cls+'"'+title+' onclick="activateOrPushScene(event,\\''+rn+'\\',\\''+rc.hue_room_id+'\\',\\''+sceneName.replace(/'/g,"\\\\'")+'\\',' + (hasScene?'true':'false') + ')">'
          +'<span>'+rn+'</span>'+badge
          +'</div>';
      }).join('');"""

if old_rooms_map in c:
    c = c.replace(old_rooms_map, new_rooms_map)
    print("rooms map updated OK")
else:
    print("rooms map NOT FOUND")

# Nouvelle fonction activateOrPushScene
old_activate = "async function activateSceneInRoom(event, roomName, roomId, sceneName) {"
new_activate = """async function activateOrPushScene(event, roomName, roomId, sceneName, hasScene) {
  event.stopPropagation();
  var item = event.currentTarget;
  if (!hasScene) {
    // D'abord pousser sur le bridge
    item.innerHTML = '<span>'+roomName+'</span><span class="scene-room-badge missing">⏳</span>';
    try {
      var r1 = await fetch('/push-scene-to-room', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({scene_name: sceneName, room_id: roomId, room_name: roomName})
      });
      var d1 = await r1.json();
      if (d1.status !== 'ok') {
        item.innerHTML = '<span>'+roomName+'</span><span class="scene-room-badge missing">✗</span>';
        return;
      }
    } catch(e) {
      item.innerHTML = '<span>'+roomName+'</span><span class="scene-room-badge missing">✗</span>';
      return;
    }
  }
  // Activer
  await activateSceneInRoom(event, roomName, roomId, sceneName);
}

async function activateSceneInRoom(event, roomName, roomId, sceneName) {"""

if old_activate in c:
    c = c.replace(old_activate, new_activate)
    print("activateOrPushScene OK")
else:
    print("activateOrPushScene NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("not-present CSS:", "not-present" in c)
print("activateOrPushScene:", "activateOrPushScene" in c)
print("hasScene:", "hasScene" in c)
