import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS
css = """
/* ACTIVATE SCENE IN HEADER */
.room-header-activate{display:flex;align-items:center;gap:6px;flex:1;margin:0 10px}
.room-activate-select{flex:1;background:#151515;border:1px solid #222;border-radius:6px;color:#ccc;font-size:11px;padding:3px 6px;font-family:inherit;outline:none;cursor:pointer;max-width:200px}
.room-activate-select:focus{border-color:#2d5a45}
.room-activate-btn{background:#1d3028;border:1px solid #2d5a45;border-radius:6px;color:#5dcaa5;font-size:11px;padding:3px 8px;cursor:pointer;white-space:nowrap;transition:background .15s;flex-shrink:0}
.room-activate-btn:hover{background:#2d5a45;color:#fff}
"""
c = c.replace("</style>", css + "\n</style>")

# 2. Dans render(), modifier le room-header pour ajouter le select activate
old_header = """      return `<div class="room-card${isModified?' modified':''}${isExp?' expanded':''}">
        <div class="room-header" onclick="toggleRoom('${roomName}')">
          <i class="ti ti-device-speaker" style="font-size:14px;color:#555"></i>
          <span class="room-name">${roomName}</span>
          <button class="room-toggle${isEnabled?' on':''}" onclick="event.stopPropagation();toggleEnabled('${roomName}')" title="${isEnabled?'Désactiver':'Activer'}"></button>
          <i class="ti ti-chevron-down chevron"></i>
        </div>"""

new_header = """      const activateHtml = (isEnabled && hueRoomId) ? `
        <div class="room-header-activate" onclick="event.stopPropagation()">
          <select class="room-activate-select" id="act-select-${safeRoomName}">
            <option value="">Chargement...</option>
          </select>
          <button class="room-activate-btn" onclick="event.stopPropagation();activateRoomScene('${roomName}','${hueRoomId}')">▶ Activer</button>
        </div>` : '';
      return `<div class="room-card${isModified?' modified':''}${isExp?' expanded':''}">
        <div class="room-header" onclick="toggleRoom('${roomName}')">
          <i class="ti ti-device-speaker" style="font-size:14px;color:#555"></i>
          <span class="room-name">${roomName}</span>
          ${activateHtml}
          <button class="room-toggle${isEnabled?' on':''}" onclick="event.stopPropagation();toggleEnabled('${roomName}')" title="${isEnabled?'Désactiver':'Activer'}"></button>
          <i class="ti ti-chevron-down chevron"></i>
        </div>"""

if old_header in c:
    c = c.replace(old_header, new_header)
    print("Header updated OK")
else:
    print("Header NOT FOUND")

# 3. Dans loadRoomScenes, aussi peupler le select activate
old_load = """    roomScenesCache[roomName] = scenes;
    sel.innerHTML = scenes.length === 0
      ? '<option value="">Aucune scène sur le bridge</option>'
      : scenes.map(function(s) {
          return '<option value="'+s.id+'">'+s.name+'</option>';
        }).join('');
    if (cnt) cnt.textContent = scenes.length + ' scène(s)';"""

new_load = """    roomScenesCache[roomName] = scenes;
    var optionsHtml = scenes.length === 0
      ? '<option value="">Aucune scène sur le bridge</option>'
      : scenes.map(function(s) {
          return '<option value="'+s.id+'" data-name="'+s.name+'">'+s.name+'</option>';
        }).join('');
    sel.innerHTML = optionsHtml;
    if (cnt) cnt.textContent = scenes.length + ' scène(s)';
    // Peupler aussi le select activate dans le header
    var actSel = document.getElementById('act-select-'+safeId);
    if (actSel) actSel.innerHTML = scenes.length === 0
      ? '<option value="">Aucune scène</option>'
      : scenes.map(function(s) {
          return '<option value="'+s.name+'">'+s.name+'</option>';
        }).join('');"""

if old_load in c:
    c = c.replace(old_load, new_load)
    print("loadRoomScenes updated OK")
else:
    print("loadRoomScenes NOT FOUND")

# 4. Aussi charger les scènes pour les rooms NON expanded (pour le select activate)
old_timeout = """    setTimeout(function() {
      Object.entries(currentConfig.rooms).forEach(function([rn, rc]) {
        if (expanded[rn] && rc.hue_room_id) loadRoomScenes(rn, rc.hue_room_id);
      });
    }, 50);"""

new_timeout = """    setTimeout(function() {
      Object.entries(currentConfig.rooms).forEach(function([rn, rc]) {
        if (rc.hue_room_id && rc.enabled !== false) loadRoomScenes(rn, rc.hue_room_id);
      });
    }, 50);"""

if old_timeout in c:
    c = c.replace(old_timeout, new_timeout)
    print("Timeout updated OK")
else:
    print("Timeout NOT FOUND")

# 5. Fonction activateRoomScene
activate_fn = """
async function activateRoomScene(roomName, roomId) {
  var safeId = roomName.replace(/\\s+/g,'_');
  var sel = document.getElementById('act-select-'+safeId);
  if (!sel || !sel.value) return;
  var sceneName = sel.value;
  try {
    var r = await fetch('/activate-hue-scene', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({room_id: roomId, scene_name: sceneName})
    });
    var data = await r.json();
    if (data.status === 'ok') {
      showToast('Scene "'+sceneName+'" activée dans '+roomName);
    } else {
      showToast('Erreur : '+(data.error||data.message), true);
    }
  } catch(e) {
    showToast('Erreur réseau', true);
  }
}
"""

c = c.replace("// \u2500\u2500\u2500 FIN GESTIONNAIRE", activate_fn + "\n// \u2500\u2500\u2500 FIN GESTIONNAIRE")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("activateRoomScene:", "activateRoomScene" in c)
print("room-header-activate CSS:", "room-header-activate" in c)
print("act-select:", "act-select-" in c)
