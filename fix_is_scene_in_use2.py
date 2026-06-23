with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

import re

old = """function isSceneInUse(sceneName) {
  if (!currentConfig || !currentConfig.rooms) return false;
  return Object.values(currentConfig.rooms).some(function(room) {
    if (!room.scenes) return false;
    return Object.values(room.scenes).some(function(styleScenes) {
      return Array.isArray(styleScenes) && styleScenes.indexOf(sceneName) >= 0;
    });
  });
}"""

new = """function isSceneInUse(sceneName) {
  if (!currentConfig) return false;
  var inRoom = Object.values(currentConfig.rooms || {}).some(function(room) {
    if (!room.scenes) return false;
    return Object.values(room.scenes).some(function(ss) {
      return Array.isArray(ss) && ss.indexOf(sceneName) >= 0;
    });
  });
  if (inRoom) return true;
  return (currentConfig.styles || []).some(function(style) {
    return Array.isArray(style.scenes) && style.scenes.indexOf(sceneName) >= 0;
  });
}"""

if old in c:
    c = c.replace(old, new)
    print("OK - replaced")
else:
    # Remplacer via regex
    c = re.sub(
        r'function isSceneInUse\(sceneName\) \{.*?\}',
        new,
        c, flags=re.DOTALL
    )
    print("OK - regex replaced")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("style.scenes check:", "style.scenes" in c)
