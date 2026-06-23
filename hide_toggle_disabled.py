import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# Trouver le bouton room-toggle et le conditionner à isEnabled
old = """          ${roomCfg._activeScene ? `<span class="room-active-scene">${roomCfg._activeScene}</span>` : ''}
          <button class="room-toggle${roomLightOn?' on':''}" onclick="event.stopPropagation();toggleRoomLight('${roomName}','${hueRoomId}',${roomLightOn})" title="${roomLightOn?'Éteindre les lumières':'Allumer les lumières'}"></button>"""

new = """          ${isEnabled && roomCfg._activeScene ? `<span class="room-active-scene">${roomCfg._activeScene}</span>` : ''}
          ${isEnabled ? `<button class="room-toggle${roomLightOn?' on':''}" onclick="event.stopPropagation();toggleRoomLight('${roomName}','${hueRoomId}',${roomLightOn})" title="${roomLightOn?'Éteindre les lumières':'Allumer les lumières'}"></button>` : ''}"""

if old in c:
    c = c.replace(old, new)
    print("OK")
else:
    print("NOT FOUND")
    # Debug
    idx = c.find("room-toggle${roomLightOn")
    print("room-toggle at:", idx)
    print(repr(c[idx-100:idx+200]))

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)
