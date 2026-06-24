import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS
css = """
/* ICONE PIECE SUR CARTE SCENARIO */
.scene-room-btn{
  position:absolute;top:7px;left:7px;
  width:22px;height:22px;border-radius:50%;
  background:rgba(0,0,0,.6);border:1px solid rgba(255,255,255,.2);
  display:none;align-items:center;justify-content:center;
  cursor:pointer;font-size:11px;
  transition:background .15s;z-index:10;
}
.scene-card:hover .scene-room-btn{display:flex}
.scene-room-btn:hover{background:rgba(29,90,69,.85)!important}
.scene-room-dropdown{
  position:absolute;top:32px;left:7px;
  background:#1a1a1a;border:1px solid #333;border-radius:10px;
  z-index:300;min-width:160px;
  box-shadow:0 8px 24px rgba(0,0,0,.7);
  overflow:hidden;
}
.scene-room-dropdown-item{
  display:flex;align-items:center;gap:8px;
  padding:8px 12px;cursor:pointer;font-size:11px;color:#ccc;
  transition:background .1s;
}
.scene-room-dropdown-item:hover{background:#252525;color:#5dcaa5}
.scene-room-dropdown-item.activating{color:#f5a623}
.scene-room-dropdown-title{
  font-size:10px;color:#444;padding:6px 12px 4px;
  text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #222;
}
"""
c = c.replace("</style>", css + "\n</style>")

# 2. Dans renderSceneCard, ajouter le bouton pièce
old_card_return = """  const isCustom = !!scene.custom;
  const inUse = isSceneInUse(scene.name);
  const safeColors = encodeURIComponent(JSON.stringify(scene.colors||[]));
  const deleteBtn = inUse"""

new_card_return = """  const isCustom = !!scene.custom;
  const inUse = isSceneInUse(scene.name);
  const safeColors = encodeURIComponent(JSON.stringify(scene.colors||[]));
  // Pièces qui ont ce scénario sur le bridge
  const sceneRooms = Object.entries(currentConfig.rooms || {}).filter(function([rn, rc]) {
    return rc.enabled !== false && rc.hue_room_id;
  }).map(function([rn, rc]) { return rn; });
  const roomBtn = sceneRooms.length > 0
    ? '<div class="scene-room-btn" onclick="event.stopPropagation();toggleSceneRoomMenu(this,\\''+scene.name.replace(/'/g,"\\\\'")+'\\')" title="Activer dans une pièce">🏠</div>'
    : '';
  const deleteBtn = inUse"""

if old_card_return in c:
    c = c.replace(old_card_return, new_card_return)
    print("Card return updated OK")
else:
    print("Card return NOT FOUND")

# 3. Ajouter roomBtn dans le HTML de la carte
old_card_html = """    ${isCustom ? `<div class="delete-btn" onclick="event.stopPropagation();deleteAnyScene('${scene.name.replace(/'/g,"\\'")}')" title="Supprimer ce scénario">✕</div>` : ''}
  </div>`;"""

new_card_html = """    ${isCustom ? `<div class="delete-btn" onclick="event.stopPropagation();deleteAnyScene('${scene.name.replace(/'/g,"\\'")}')" title="Supprimer ce scénario">✕</div>` : ''}
    ${roomBtn}
  </div>`;"""

if old_card_html in c:
    c = c.replace(old_card_html, new_card_html)
    print("Card HTML updated OK")
else:
    print("Card HTML NOT FOUND")

# 4. JS - toggleSceneRoomMenu + activateSceneInRoom
room_menu_js = """
// ─── MENU ACTIVATION PIECE ──────────────────────────────────────
function toggleSceneRoomMenu(btn, sceneName) {
  // Fermer tous les autres menus ouverts
  document.querySelectorAll('.scene-room-dropdown').forEach(function(d){ d.remove(); });
  
  // Si ce bouton avait déjà un menu ouvert, on s'arrête là
  if (btn._menuOpen) { btn._menuOpen = false; return; }
  btn._menuOpen = true;

  var rooms = Object.entries(currentConfig.rooms || {}).filter(function([rn, rc]) {
    return rc.enabled !== false && rc.hue_room_id;
  });

  var dropdown = document.createElement('div');
  dropdown.className = 'scene-room-dropdown';
  dropdown.innerHTML = '<div class="scene-room-dropdown-title">Activer dans</div>'
    + rooms.map(function([rn, rc]) {
        return '<div class="scene-room-dropdown-item" onclick="activateSceneInRoom(event,\\''+rn+'\\',\\''+rc.hue_room_id+'\\',\\''+sceneName.replace(/'/g,"\\\\'")+'\\')">'
          +'<span>'+rn+'</span>'
          +'</div>';
      }).join('');

  btn.appendChild(dropdown);

  // Fermer au clic extérieur
  setTimeout(function() {
    document.addEventListener('click', function handler(e) {
      if (!btn.contains(e.target)) {
        dropdown.remove();
        btn._menuOpen = false;
        document.removeEventListener('click', handler);
      }
    });
  }, 10);
}

async function activateSceneInRoom(event, roomName, roomId, sceneName) {
  event.stopPropagation();
  var item = event.currentTarget;
  item.classList.add('activating');
  item.textContent = '⏳ '+roomName+'...';
  try {
    var r = await fetch('/activate-hue-scene', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({room_id: roomId, scene_name: sceneName})
    });
    var data = await r.json();
    if (data.status === 'ok') {
      item.textContent = '✓ '+roomName;
      item.style.color = '#5dcaa5';
      currentConfig.rooms[roomName]._lightOn = true;
      setTimeout(function() {
        document.querySelectorAll('.scene-room-dropdown').forEach(function(d){ d.remove(); });
        render();
      }, 800);
      showToast('"'+sceneName+'" activée dans '+roomName);
    } else {
      item.textContent = '✗ Erreur';
      item.style.color = '#e05555';
    }
  } catch(e) {
    item.textContent = '✗ Réseau';
    item.style.color = '#e05555';
  }
}
// ─── FIN MENU ACTIVATION PIECE ───────────────────────────────────
"""

c = c.replace("// \u2500\u2500\u2500 FIN GESTIONNAIRE", room_menu_js + "\n// \u2500\u2500\u2500 FIN GESTIONNAIRE")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("scene-room-btn CSS:", "scene-room-btn" in c)
print("toggleSceneRoomMenu:", "toggleSceneRoomMenu" in c)
print("activateSceneInRoom:", "activateSceneInRoom" in c)
