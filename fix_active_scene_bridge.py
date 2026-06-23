with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# Remplacer la logique de stockage _activeScene
old = """      if (data.active_scene) {
        currentConfig.rooms[roomName]._activeScene = data.active_scene;
        try { sessionStorage.setItem("activeScene_"+roomName, data.active_scene); } catch(e){}
      } else {
        try { var stored = sessionStorage.getItem("activeScene_"+roomName); if(stored) currentConfig.rooms[roomName]._activeScene = stored; } catch(e){}
      }"""

new = """      // Toujours utiliser l'etat reel du bridge
      currentConfig.rooms[roomName]._activeScene = data.active_scene || null;"""

if old in c:
    c = c.replace(old, new)
    print("loadRoomLightStates OK")
else:
    print("NOT FOUND")

# Supprimer aussi les sessionStorage dans activateRoomScene et toggleRoomLight
# car on se fie desormais uniquement au bridge
import re
c = re.sub(r"\s*try \{ sessionStorage\.(setItem|removeItem)\([^)]+\); \} catch\(e\) \{\}", "", c)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("sessionStorage removed:", "sessionStorage" not in c)
