with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# Fix activateRoomScene - mettre à jour _lightOn après activation
old = """    if (data.status === 'ok') {
      showToast('"'+sceneName+'" activée dans '+roomName);
    } else {"""

new = """    if (data.status === 'ok') {
      currentConfig.rooms[roomName]._lightOn = true;
      render();
      showToast('"'+sceneName+'" activée dans '+roomName);
    } else {"""

if old in c:
    c = c.replace(old, new)
    print("activateRoomScene OK")
else:
    print("NOT FOUND activateRoomScene")

# Fix toggleRoomLight - showToast correct
old2 = "      showToast(turnOn ? roomName+' allumée (Lumineux)' : roomName+' éteinte');"
new2 = "      showToast(turnOn ? roomName+' : allumée' : roomName+' : éteinte');"
if old2 in c:
    c = c.replace(old2, new2)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("_lightOn update:", "currentConfig.rooms[roomName]._lightOn = true" in c)
