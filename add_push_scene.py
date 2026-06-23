import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS
css = """
.room-scene-add{padding:8px 14px 12px;background:#0d0d0d}
.room-scene-add-title{font-size:10px;color:#444;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
.room-scene-add-row{display:flex;align-items:center;gap:8px}
.room-scene-add-select{flex:1;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;color:#ccc;font-size:11px;padding:5px 8px;font-family:inherit;outline:none;cursor:pointer}
.room-scene-add-select:focus{border-color:#2d5a45}
.room-scene-add-btn{background:#1d3028;border:1px solid #2d5a45;border-radius:6px;color:#5dcaa5;font-size:11px;padding:5px 10px;cursor:pointer;white-space:nowrap;transition:background .15s}
.room-scene-add-btn:hover{background:#2d5a45;color:#fff}
.room-scene-add-result{font-size:10px;margin-top:4px;min-height:14px}
.room-scene-add-result.ok{color:#5dcaa5}
.room-scene-add-result.err{color:#e05555}
"""
c = c.replace("</style>", css + "\n</style>")

# 2. Dans le HTML généré par render(), ajouter le bloc "Ajouter" après le bloc "Supprimer"
old_manager = """        const managerHtml = hueRoomId ? `<div class="room-scene-manager">
          <div class="room-scene-manager-title">🗑 Supprimer une scène</div>
          <div class="room-scene-manager-row">
            <select class="room-scene-select" id="mgr-select-${roomName.replace(/\\s+/g,'_')}">
              <option value="">Chargement...</option>
            </select>
            <span class="room-scene-count" id="mgr-count-${roomName.replace(/\\s+/g,'_')}"></span>
            <button class="room-scene-del" onclick="deleteRoomScene('${roomName}','${hueRoomId}')">🗑 Supprimer</button>
          </div>
        </div>` : '';"""

new_manager = """        const safeRoomName = roomName.replace(/\\s+/g,'_');
        const addOptions = knownScenes.map(function(s) {
          return '<option value="'+encodeURIComponent(s.name)+'">'+s.name+'</option>';
        }).join('');
        const managerHtml = hueRoomId ? `<div class="room-scene-manager">
          <div class="room-scene-manager-title">🗑 Supprimer une scène</div>
          <div class="room-scene-manager-row">
            <select class="room-scene-select" id="mgr-select-${safeRoomName}">
              <option value="">Chargement...</option>
            </select>
            <span class="room-scene-count" id="mgr-count-${safeRoomName}"></span>
            <button class="room-scene-del" onclick="deleteRoomScene('${roomName}','${hueRoomId}')">🗑 Supprimer</button>
          </div>
        </div>
        <div class="room-scene-add">
          <div class="room-scene-add-title">➕ Ajouter une scène sur le bridge</div>
          <div class="room-scene-add-row">
            <select class="room-scene-add-select" id="add-select-${safeRoomName}">${addOptions}</select>
            <button class="room-scene-add-btn" onclick="pushSceneToBridge('${roomName}','${hueRoomId}')">➕ Ajouter</button>
          </div>
          <div class="room-scene-add-result" id="add-result-${safeRoomName}"></div>
        </div>` : '';"""

if old_manager in c:
    c = c.replace(old_manager, new_manager)
    print("Manager HTML updated OK")
else:
    print("Manager HTML NOT FOUND")

# 3. Endpoint backend - ajouter pushSceneToBridge JS
push_js = """
async function pushSceneToBridge(roomName, roomId) {
  var safeId = roomName.replace(/\\s+/g,'_');
  var sel = document.getElementById('add-select-'+safeId);
  var resultEl = document.getElementById('add-result-'+safeId);
  if (!sel || !sel.value) return;
  var sceneName = decodeURIComponent(sel.value);
  var scene = knownScenes.find(function(s){ return s.name === sceneName; });
  if (!scene) { resultEl.textContent = 'Scénario introuvable'; resultEl.className='room-scene-add-result err'; return; }
  resultEl.textContent = 'Envoi en cours...'; resultEl.className='room-scene-add-result';
  try {
    var r = await fetch('/push-scene-to-room', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({scene_name: sceneName, room_id: roomId, room_name: roomName})
    });
    var data = await r.json();
    if (data.status === 'ok') {
      resultEl.textContent = '✓ "'+sceneName+'" ajouté sur le bridge';
      resultEl.className = 'room-scene-add-result ok';
      setTimeout(function(){ loadRoomScenes(roomName, roomId); }, 500);
    } else {
      resultEl.textContent = 'Erreur : '+data.message;
      resultEl.className = 'room-scene-add-result err';
    }
  } catch(e) {
    resultEl.textContent = 'Erreur réseau';
    resultEl.className = 'room-scene-add-result err';
  }
}
"""

c = c.replace("// \u2500\u2500\u2500 FIN GESTIONNAIRE", push_js + "\n// \u2500\u2500\u2500 FIN GESTIONNAIRE")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("pushSceneToBridge JS:", "pushSceneToBridge" in c)
print("room-scene-add CSS:", "room-scene-add{" in c)
print("add-select:", "add-select-" in c)
