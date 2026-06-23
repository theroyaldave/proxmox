import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS
css = """
/* GESTIONNAIRE SCENES PAR PIECE */
.room-scene-manager{padding:8px 14px 4px;border-bottom:1px solid #1a1a1a;background:#0d0d0d}
.room-scene-manager-title{font-size:10px;color:#444;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
.room-scene-manager-row{display:flex;align-items:center;gap:8px}
.room-scene-select{flex:1;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;color:#ccc;font-size:11px;padding:5px 8px;font-family:inherit;outline:none;cursor:pointer}
.room-scene-select:focus{border-color:#2d5a45}
.room-scene-del{background:rgba(90,45,45,.85);border:1px solid rgba(255,80,80,.3);border-radius:6px;color:#e05555;font-size:11px;padding:5px 10px;cursor:pointer;white-space:nowrap;transition:background .15s}
.room-scene-del:hover{background:rgba(150,45,45,.9)}
.room-scene-count{font-size:10px;color:#444;white-space:nowrap}
"""
c = c.replace("</style>", css + "\n</style>")

# 2. Dans render(), ajouter le gestionnaire dans chaque room-card expanded
# Chercher bodyContent = et ajouter le gestionnaire avant styles-grid
old_body = """      if (!isEnabled) {
        bodyContent = `<div class="room-disabled-msg">Pièce désactivée — les lumières ne seront pas contrôlées.</div>`;
      } else {
        const stylesHtml = currentConfig.styles.map(style => {"""

new_body = """      const hueRoomId = roomCfg.hue_room_id || '';
      if (!isEnabled) {
        bodyContent = `<div class="room-disabled-msg">Pièce désactivée — les lumières ne seront pas contrôlées.</div>`;
      } else {
        const managerHtml = hueRoomId ? `<div class="room-scene-manager">
          <div class="room-scene-manager-title">🗑 Scènes sur le bridge</div>
          <div class="room-scene-manager-row">
            <select class="room-scene-select" id="mgr-select-${roomName.replace(/\\s+/g,'_')}">
              <option value="">Chargement...</option>
            </select>
            <span class="room-scene-count" id="mgr-count-${roomName.replace(/\\s+/g,'_')}"></span>
            <button class="room-scene-del" onclick="deleteRoomScene('${roomName}','${hueRoomId}')">🗑 Supprimer</button>
          </div>
        </div>` : '';
        const stylesHtml = currentConfig.styles.map(style => {"""

if old_body in c:
    c = c.replace(old_body, new_body)
    print("Body updated OK")
else:
    print("Body NOT FOUND")

# 3. Ajouter managerHtml dans le bodyContent
old_body_content = '        bodyContent = `<div class="styles-grid">${stylesHtml}</div>`;'
new_body_content = '        bodyContent = managerHtml + `<div class="styles-grid">${stylesHtml}</div>`;'
if old_body_content in c:
    c = c.replace(old_body_content, new_body_content)
    print("bodyContent updated OK")
else:
    print("bodyContent NOT FOUND")

# 4. Après render(), charger les scènes pour les rooms expanded
old_render_end = """  const _fi = document.getElementById('footer-info');
  if (_fi) {
    _fi.textContent = modified ? 'Modifications non sauvegardées' : 'Aucune modification';
    _fi.className = 'rooms-footer-info' + (modified ? ' modified' : '');
  }"""

new_render_end = """  const _fi = document.getElementById('footer-info');
  if (_fi) {
    _fi.textContent = modified ? 'Modifications non sauvegardées' : 'Aucune modification';
    _fi.className = 'rooms-footer-info' + (modified ? ' modified' : '');
  }
  // Charger les scènes bridge pour les rooms expanded
  Object.entries(currentConfig.rooms).forEach(function([roomName, roomCfg]) {
    if (expanded[roomName] && roomCfg.hue_room_id) {
      loadRoomScenes(roomName, roomCfg.hue_room_id);
    }
  });"""

if old_render_end in c:
    c = c.replace(old_render_end, new_render_end)
    print("render end updated OK")
else:
    print("render end NOT FOUND")

# 5. JS fonctions
js = """
// ─── GESTIONNAIRE SCÈNES PAR PIÈCE ──────────────────────────────
var roomScenesCache = {};

async function loadRoomScenes(roomName, roomId) {
  var safeId = roomName.replace(/\\s+/g,'_');
  var sel = document.getElementById('mgr-select-'+safeId);
  var cnt = document.getElementById('mgr-count-'+safeId);
  if (!sel) return;
  sel.innerHTML = '<option value="">Chargement...</option>';
  try {
    var r = await fetch('/hue-get-room-scenes?room_id='+roomId);
    var data = await r.json();
    var scenes = data.scenes || [];
    roomScenesCache[roomName] = scenes;
    sel.innerHTML = scenes.length === 0
      ? '<option value="">Aucune scène sur le bridge</option>'
      : scenes.map(function(s) {
          return '<option value="'+s.id+'">'+s.name+'</option>';
        }).join('');
    if (cnt) cnt.textContent = scenes.length + ' scène(s)';
  } catch(e) {
    sel.innerHTML = '<option value="">Erreur de chargement</option>';
  }
}

async function deleteRoomScene(roomName, roomId) {
  var safeId = roomName.replace(/\\s+/g,'_');
  var sel = document.getElementById('mgr-select-'+safeId);
  if (!sel || !sel.value) { alert('Sélectionnez une scène à supprimer.'); return; }
  var sceneName = sel.options[sel.selectedIndex].text;
  if (!confirm('Supprimer "'+sceneName+'" de '+roomName+' ?')) return;
  try {
    var r = await fetch('/hue-delete-room-scene', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({scene_id: sel.value})
    });
    var data = await r.json();
    if (data.status === 'ok') {
      showToast('"'+sceneName+'" supprimé de '+roomName);
      loadRoomScenes(roomName, roomId);
    } else {
      showToast('Erreur : '+data.message, true);
    }
  } catch(e) {
    showToast('Erreur réseau', true);
  }
}
// ─── FIN GESTIONNAIRE ────────────────────────────────────────────
"""

c = c.replace("// ─── CUSTOM SELECT ───", js + "\n// ─── CUSTOM SELECT ───")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("room-scene-manager:", "room-scene-manager" in c)
print("loadRoomScenes:", "loadRoomScenes" in c)
print("deleteRoomScene:", "deleteRoomScene" in c)
