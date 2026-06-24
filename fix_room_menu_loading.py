with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. Dans toggleSceneRoomMenu, afficher "Chargement..." si roomScenesCache pas prêt
old_rooms_filter = """  var rooms = Object.entries(currentConfig.rooms || {}).filter(function([rn, rc]) {
    return rc.enabled !== false && rc.hue_room_id;
  });"""

new_rooms_filter = """  var rooms = Object.entries(currentConfig.rooms || {}).filter(function([rn, rc]) {
    return rc.enabled !== false && rc.hue_room_id;
  });

  // Vérifier si les scènes sont chargées pour toutes les pièces
  var allLoaded = rooms.every(function([rn]) { return roomScenesCache[rn] !== undefined; });
  if (!allLoaded) {
    var dropdown = document.createElement('div');
    dropdown.className = 'scene-room-dropdown';
    var rect2 = btn.getBoundingClientRect();
    dropdown.style.top = (rect2.bottom + 4) + 'px';
    dropdown.style.left = rect2.left + 'px';
    dropdown.innerHTML = '<div class="scene-room-dropdown-title">Chargement des pièces...</div>';
    document.body.appendChild(dropdown);
    setTimeout(function() {
      if (dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
      btn._menuOpen = false;
    }, 1500);
    return;
  }"""

if old_rooms_filter in c:
    c = c.replace(old_rooms_filter, new_rooms_filter)
    print("Loading check OK")
else:
    print("rooms filter NOT FOUND")

# 2. Dans activateOrPushScene, désactiver le bouton pendant l'opération pour éviter les doublons
old_push_start = """  if (!hasScene) {
    // D'abord pousser sur le bridge
    item.innerHTML = '<span>'+roomName+'</span><span class="scene-room-badge missing">⏳</span>';"""

new_push_start = """  if (!hasScene) {
    // Désactiver pour éviter les doublons
    item.style.pointerEvents = 'none';
    // D'abord pousser sur le bridge
    item.innerHTML = '<span>'+roomName+'</span><span class="scene-room-badge missing">⏳</span>';"""

if old_push_start in c:
    c = c.replace(old_push_start, new_push_start)
    print("Disable during push OK")
else:
    print("push start NOT FOUND")

# 3. Mettre à jour roomScenesCache après push réussi
old_after_push = """      if (d1.status !== 'ok') {
        item.innerHTML = '<span>'+roomName+'</span><span class="scene-room-badge missing">✗</span>';
        return;
      }"""

new_after_push = """      if (d1.status !== 'ok') {
        item.innerHTML = '<span>'+roomName+'</span><span class="scene-room-badge missing">✗</span>';
        item.style.pointerEvents = '';
        return;
      }
      // Mettre à jour le cache local
      if (!roomScenesCache[roomName]) roomScenesCache[roomName] = [];
      roomScenesCache[roomName].push({id: 'pending', name: sceneName});"""

if old_after_push in c:
    c = c.replace(old_after_push, new_after_push)
    print("Cache update after push OK")
else:
    print("after push NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("allLoaded check:", "allLoaded" in c)
print("pointerEvents:", "pointerEvents" in c)
