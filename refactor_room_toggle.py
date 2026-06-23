import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS - nouveau bouton config enable/disable
css = """
/* TOGGLE LUMIERE vs CONFIG */
.room-config-toggle{
  font-size:10px;padding:4px 10px;border-radius:6px;cursor:pointer;
  border:1px solid #333;background:#1a1a1a;color:#666;
  transition:all .15s;white-space:nowrap;flex-shrink:0;
}
.room-config-toggle.enabled{border-color:#c0392b;color:#e05555;background:rgba(192,57,43,.1)}
.room-config-toggle.enabled:hover{background:rgba(192,57,43,.25)}
.room-config-toggle.disabled{border-color:#2d5a45;color:#5dcaa5;background:rgba(29,90,69,.1)}
.room-config-toggle.disabled:hover{background:rgba(29,90,69,.25)}
"""
c = c.replace("</style>", css + "\n</style>")

# 2. Modifier le toggle dans le header → contrôle lumières
# Le toggle actuel appelle toggleEnabled — on le remplace par toggleRoomLight
old_toggle_btn = """          <button class="room-toggle${isEnabled?' on':''}" onclick="event.stopPropagation();toggleEnabled('${roomName}')" title="${isEnabled?'Désactiver':'Activer'}"></button>"""

new_toggle_btn = """          <button class="room-toggle${roomLightOn?' on':''}" onclick="event.stopPropagation();toggleRoomLight('${roomName}','${hueRoomId}',${roomLightOn})" title="${roomLightOn?'Éteindre les lumières':'Allumer les lumières'}"></button>"""

if old_toggle_btn in c:
    c = c.replace(old_toggle_btn, new_toggle_btn)
    print("Toggle btn updated OK")
else:
    print("Toggle btn NOT FOUND")

# 3. Ajouter roomLightOn dans le render
old_room_start = "      const hueRoomId = roomCfg.hue_room_id || '';"
new_room_start = """      const hueRoomId = roomCfg.hue_room_id || '';
      const roomLightOn = roomCfg._lightOn !== false;"""

if old_room_start in c:
    c = c.replace(old_room_start, new_room_start, 1)
    print("roomLightOn added OK")
else:
    print("roomLightOn NOT FOUND")

# 4. Ajouter bouton config dans le bodyContent (quand pièce expanded)
old_body_content = '        bodyContent = managerHtml + `<div class="styles-grid">${stylesHtml}</div>`;'
new_body_content = """        const configToggleHtml = `<div style="padding:8px 14px 0;text-align:right">
          <button class="room-config-toggle enabled" onclick="toggleEnabled('${roomName}')" title="Exclure cette pièce du contrôle automatique">
            ⚙ Exclure de la config
          </button>
        </div>`;
        bodyContent = configToggleHtml + managerHtml + `<div class="styles-grid">${stylesHtml}</div>`;"""

if old_body_content in c:
    c = c.replace(old_body_content, new_body_content)
    print("Config toggle added OK")
else:
    print("Config toggle NOT FOUND")

# 5. Aussi modifier le bodyContent quand isEnabled=false
old_disabled = '        bodyContent = `<div class="room-disabled-msg">Pièce désactivée — les lumières ne seront pas contrôlées.</div>`;'
new_disabled = """        bodyContent = `<div style="padding:8px 14px 0;text-align:right">
          <button class="room-config-toggle disabled" onclick="toggleEnabled('${roomName}')" title="Inclure cette pièce dans le contrôle automatique">
            ⚙ Inclure dans la config
          </button>
        </div><div class="room-disabled-msg">Pièce désactivée — les lumières ne seront pas contrôlées.</div>`;"""

if old_disabled in c:
    c = c.replace(old_disabled, new_disabled)
    print("Disabled config toggle added OK")
else:
    print("Disabled config toggle NOT FOUND")

# 6. JS - toggleRoomLight
toggle_light_fn = """
async function toggleRoomLight(roomName, roomId, currentlyOn) {
  if (!roomId) return;
  var turnOn = !currentlyOn;
  try {
    var r = await fetch('/hue-toggle-room', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({room_id: roomId, on: turnOn})
    });
    var data = await r.json();
    if (data.status === 'ok') {
      // Mettre à jour l'état local
      currentConfig.rooms[roomName]._lightOn = turnOn;
      render();
      showToast(turnOn ? roomName+' allumée (Lumineux)' : roomName+' éteinte');
    } else {
      showToast('Erreur : '+data.message, true);
    }
  } catch(e) {
    showToast('Erreur réseau', true);
  }
}
"""

c = c.replace("// \u2500\u2500\u2500 FIN GESTIONNAIRE", toggle_light_fn + "\n// \u2500\u2500\u2500 FIN GESTIONNAIRE")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("toggleRoomLight:", "toggleRoomLight" in c)
print("room-config-toggle CSS:", "room-config-toggle" in c)
print("hue-toggle-room fetch:", "hue-toggle-room" in c)
