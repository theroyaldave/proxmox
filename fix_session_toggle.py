with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

old = """      if (!turnOn) currentConfig.rooms[roomName]._activeScene = null;
      else currentConfig.rooms[roomName]._activeScene = 'Lumineux';"""

new = """      if (!turnOn) {
        currentConfig.rooms[roomName]._activeScene = null;
        try { sessionStorage.removeItem('activeScene_'+roomName); } catch(e) {}
      } else {
        currentConfig.rooms[roomName]._activeScene = 'Lumineux';
        try { sessionStorage.setItem('activeScene_'+roomName, 'Lumineux'); } catch(e) {}
      }"""

if old in c:
    c = c.replace(old, new)
    print("OK")
else:
    print("NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)
