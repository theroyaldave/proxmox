with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. startPreview - ajouter brightness param
old_start = "function startPreview(colors, speed, sceneName) {"
new_start = "function startPreview(colors, speed, sceneName, brightness) {"

c = c.replace(old_start, new_start)

# 2. Stocker brightness dans previewBrightness
old_preview_vars = """var previewColors = [];
var previewSpeed = 0.5;
var previewAnimFrame = null;
var previewColorIdx = [0, 1];
var previewT = [0, 0];
var previewLastTime = null;"""

new_preview_vars = """var previewColors = [];
var previewSpeed = 0.5;
var previewBrightness = 100;
var previewAnimFrame = null;
var previewColorIdx = [0, 1];
var previewT = [0, 0];
var previewLastTime = null;"""

if old_preview_vars in c:
    c = c.replace(old_preview_vars, new_preview_vars)
    print("previewBrightness var OK")
else:
    print("preview vars NOT FOUND")

# 3. Dans startPreview, initialiser previewBrightness
old_init_preview = """  previewColors = colors && colors.length ? colors : ['#ffffff'];
  previewSpeed = speed !== undefined ? speed : 0.5;"""

new_init_preview = """  previewColors = colors && colors.length ? colors : ['#ffffff'];
  previewSpeed = speed !== undefined ? speed : 0.5;
  previewBrightness = brightness !== undefined ? brightness : 100;"""

if old_init_preview in c:
    c = c.replace(old_init_preview, new_init_preview)
    print("startPreview brightness init OK")
else:
    print("startPreview init NOT FOUND")

# 4. Dans setBulbColor, appliquer brightness sur l'opacité du glow
old_set_bulb = """function setBulbColor(idx, color) {
  var glow = document.getElementById('bulb-glow-'+idx);
  var s0 = document.getElementById('bg'+idx+'-s0');
  var s1 = document.getElementById('bg'+idx+'-s1');
  if (glow) glow.style.background = color;
  if (s0) { s0.setAttribute('stop-color', color); s0.setAttribute('stop-opacity','1'); }
  if (s1) { s1.setAttribute('stop-color', color); s1.setAttribute('stop-opacity','0.6'); }
}"""

new_set_bulb = """function setBulbColor(idx, color) {
  var glow = document.getElementById('bulb-glow-'+idx);
  var s0 = document.getElementById('bg'+idx+'-s0');
  var s1 = document.getElementById('bg'+idx+'-s1');
  var glowOpacity = (previewBrightness / 100) * 0.7;
  var s1Opacity = (previewBrightness / 100) * 0.6;
  if (glow) { glow.style.background = color; glow.style.opacity = glowOpacity; }
  if (s0) { s0.setAttribute('stop-color', color); s0.setAttribute('stop-opacity', (previewBrightness/100).toFixed(2)); }
  if (s1) { s1.setAttribute('stop-color', color); s1.setAttribute('stop-opacity', s1Opacity.toFixed(2)); }
}"""

if old_set_bulb in c:
    c = c.replace(old_set_bulb, new_set_bulb)
    print("setBulbColor brightness OK")
else:
    print("setBulbColor NOT FOUND")

# 5. Dans handleCardClick, passer brightness
old_click = """  var scene = knownScenes.find(function(s){ return s.name === name; });
  var speed = (scene && scene.speed !== undefined) ? scene.speed : 0.5;
  startPreview(colors, speed, name);"""

new_click = """  var scene = knownScenes.find(function(s){ return s.name === name; });
  var speed = (scene && scene.speed !== undefined) ? scene.speed : 0.5;
  var brightness = (scene && scene.brightness !== undefined) ? scene.brightness : 100;
  startPreview(colors, speed, name, brightness);"""

if old_click in c:
    c = c.replace(old_click, new_click)
    print("handleCardClick brightness OK")
else:
    print("handleCardClick NOT FOUND")

# 6. Dans le bouton Aperçu du formulaire, passer brightness
old_apercu_btn = """onclick="startPreview(getActiveColors(), parseFloat(document.getElementById('create-speed').value), document.getElementById('create-name').value||'Apercu')"""
new_apercu_btn = """onclick="startPreview(getActiveColors(), parseFloat(document.getElementById('create-speed').value), document.getElementById('create-name').value||'Apercu', parseInt(document.getElementById('create-brightness').value)||100)"""

if old_apercu_btn in c:
    c = c.replace(old_apercu_btn, new_apercu_btn)
    print("Apercu button brightness OK")
else:
    print("Apercu button NOT FOUND")

# 7. Dans preview-info, afficher aussi brightness
old_info = "  if (info2) info2.textContent = previewColors.length+' couleur(s) — vitesse '+previewSpeed.toFixed(2);"
new_info = "  if (info2) info2.textContent = previewColors.length+' couleur(s) — vitesse '+previewSpeed.toFixed(2)+' — intensité '+Math.round(previewBrightness)+'%';"

if old_info in c:
    c = c.replace(old_info, new_info)
    print("preview info brightness OK")
else:
    print("preview info NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("previewBrightness:", "previewBrightness" in c)
