import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. Ajouter la fonction isSceneInUse
is_in_use_fn = """
function isSceneInUse(sceneName) {
  if (!currentConfig || !currentConfig.rooms) return false;
  return Object.values(currentConfig.rooms).some(function(room) {
    if (!room.scenes) return false;
    return Object.values(room.scenes).some(function(styleScenes) {
      return Array.isArray(styleScenes) && styleScenes.indexOf(sceneName) >= 0;
    });
  });
}
"""

c = c.replace("function isSceneInUse", "// already defined\nfunction isSceneInUse") if "function isSceneInUse" in c else c
c = c.replace("// \u2500\u2500\u2500 APERCU AMPOULES", is_in_use_fn + "\n// \u2500\u2500\u2500 APERCU AMPOULES")

# 2. Modifier renderSceneCard pour afficher le bouton delete sur toutes les cartes
# sauf si en cours d'utilisation
old_card = """  const isCustom = !!scene.custom;
  const safeColors = encodeURIComponent(JSON.stringify(scene.colors||[]));
  return `<div class="scene-card${isCustom?' custom':''}" data-colors="${safeColors}" data-name="${scene.name.replace(/"/g,'&quot;')}" onclick="handleCardClick(this)">
    ${mediaHtml}
    <div class="scene-card-overlay"></div>
    <span class="scene-card-name">${scene.name}</span>
    <span class="scene-card-badge ${isDynamic?'dynamic':'fixed'}" title="${isDynamic?'Scénario dynamique':'Scénario fixe'}">${isDynamic?'🌈':'💡'}</span>
    <div class="scene-card-bottom">
      <div class="scene-card-dots">${dotsHtml}</div>
    </div>
    ${isCustom ? `<div class="delete-btn" onclick="event.stopPropagation();deleteCustomScene('${scene.name.replace(/'/g,"\\'")}')" title="Supprimer">✕</div>` : ''}
  </div>`;"""

new_card = """  const isCustom = !!scene.custom;
  const inUse = isSceneInUse(scene.name);
  const safeColors = encodeURIComponent(JSON.stringify(scene.colors||[]));
  const deleteBtn = inUse
    ? `<div class="delete-btn" style="opacity:.3;cursor:not-allowed" title="Scénario utilisé dans un style">✕</div>`
    : `<div class="delete-btn" onclick="event.stopPropagation();deleteAnyScene('${scene.name.replace(/'/g,"\\'")}')" title="Supprimer ce scénario">✕</div>`;
  return `<div class="scene-card${isCustom?' custom':''}" data-colors="${safeColors}" data-name="${scene.name.replace(/"/g,'&quot;')}" onclick="handleCardClick(this)">
    ${mediaHtml}
    <div class="scene-card-overlay"></div>
    <span class="scene-card-name">${scene.name}</span>
    <span class="scene-card-badge ${isDynamic?'dynamic':'fixed'}" title="${isDynamic?'Scénario dynamique':'Scénario fixe'}">${isDynamic?'🌈':'💡'}</span>
    <div class="scene-card-bottom">
      <div class="scene-card-dots">${dotsHtml}</div>
    </div>
    ${deleteBtn}
  </div>`;"""

if old_card in c:
    c = c.replace(old_card, new_card)
    print("renderSceneCard updated OK")
else:
    print("renderSceneCard NOT FOUND")

# 3. Ajouter deleteAnyScene qui appelle deleteCustomScene ou delete-custom-scene selon le type
delete_any_fn = """
async function deleteAnyScene(name) {
  var scene = knownScenes.find(function(s){ return s.name === name; });
  var msg = scene && scene.custom
    ? 'Supprimer le scénario personnalisé "'+name+'" ?'
    : 'Supprimer le scénario "'+name+'" du bridge (toutes les pièces) et de la base locale ?';
  if (!(await showConfirm(msg))) return;
  try {
    var r = await fetch('/delete-custom-scene', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name: name})
    });
    var data = await r.json();
    if (data.status === 'ok') {
      knownScenes = knownScenes.filter(function(s){ return s.name !== name; });
      delete SCENE_IMAGE_MAP[name];
      render();
      showToast('"'+name+'" supprimé');
    } else {
      showToast('Erreur : '+data.message, true);
    }
  } catch(e) {
    showToast('Erreur réseau', true);
  }
}
"""

c = c.replace("// \u2500\u2500\u2500 FIN GESTIONNAIRE", delete_any_fn + "\n// \u2500\u2500\u2500 FIN GESTIONNAIRE")

# 4. CSS - afficher delete-btn sur toutes les cartes (pas seulement .custom)
c = c.replace(
    ".scene-card.custom .scene-card-badge{background:rgba(29,158,117,.85)}",
    ".scene-card.custom .scene-card-badge{background:rgba(29,158,117,.85)}\n.scene-card:hover .delete-btn{display:flex!important}"
)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("isSceneInUse:", "function isSceneInUse" in c)
print("deleteAnyScene:", "function deleteAnyScene" in c)
print("inUse check:", "isSceneInUse" in c)
