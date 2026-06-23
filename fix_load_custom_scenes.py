import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# Remplacer loadCustomScenes avec regex pour éviter les problèmes de ! dans bash
c = re.sub(
    r'async function loadCustomScenes\(\).*?^}',
    '''async function loadCustomScenes() {
  try {
    await fetch('/hue-sync-scenes', {method:'POST'}).catch(function(){});
    const r = await fetch('/custom-scenes.json?_='+Date.now());
    if (!r.ok) return;
    const data = await r.json();
    knownScenes = [];
    (data.scenes||[]).forEach(function(cs) {
      knownScenes.push({
        name: cs.name,
        colors: cs.colors || [],
        mode: cs.mode || 'dynamic_palette',
        speed: cs.speed !== undefined ? cs.speed : 0.5,
        custom: cs.custom ? true : false
      });
      if (cs.image_file) SCENE_IMAGE_MAP[cs.name] = cs.image_file;
    });
  } catch(e) { console.warn('loadCustomScenes error:', e); }
}''',
    c, flags=re.DOTALL | re.MULTILINE
)

# handleCardClick : utiliser la vraie vitesse depuis knownScenes
old_click = """function handleCardClick(el) {
  const colors = JSON.parse(decodeURIComponent(el.dataset.colors || '[]'));
  const name = el.dataset.name || '';
  const speed = 0.5;
  startPreview(colors, speed, name);
}"""

new_click = """function handleCardClick(el) {
  const colors = JSON.parse(decodeURIComponent(el.dataset.colors || '[]'));
  const name = el.dataset.name || '';
  const scene = knownScenes.find(function(s){ return s.name === name; });
  const speed = (scene && scene.speed !== undefined) ? scene.speed : 0.5;
  startPreview(colors, speed, name);
}"""

if old_click in c:
    c = c.replace(old_click, new_click)
    print("handleCardClick OK")
else:
    print("handleCardClick NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("loadCustomScenes synced:", "hue-sync-scenes" in c)
print("real speed:", "scene.speed" in c)
