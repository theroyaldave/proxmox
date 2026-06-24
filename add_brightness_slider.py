import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. HTML - ajouter slider intensité à côté du slider vitesse
old_speed_group = """          <div class="form-group">
            <label class="form-label">Vitesse de transition</label>
            <div class="speed-wrap">
              <input type="range" class="speed-slider" id="create-speed" min="0" max="1" step="0.05" value="0.5"
                oninput="document.getElementById('create-speed-val').textContent=parseFloat(this.value).toFixed(2)">
              <span class="speed-val" id="create-speed-val">0.50</span>
            </div>
            <div class="speed-labels"><span>Lent</span><span>Rapide</span></div>
          </div>"""

new_speed_group = """          <div class="form-group">
            <label class="form-label">Vitesse de transition</label>
            <div class="speed-wrap">
              <input type="range" class="speed-slider" id="create-speed" min="0" max="1" step="0.05" value="0.5"
                oninput="document.getElementById('create-speed-val').textContent=parseFloat(this.value).toFixed(2)">
              <span class="speed-val" id="create-speed-val">0.50</span>
            </div>
            <div class="speed-labels"><span>Lent</span><span>Rapide</span></div>
          </div>
          <div class="form-group">
            <label class="form-label">Intensité (brightness)</label>
            <div class="speed-wrap">
              <input type="range" class="speed-slider" id="create-brightness" min="1" max="100" step="1" value="100"
                oninput="document.getElementById('create-brightness-val').textContent=this.value+'%'">
              <span class="speed-val" id="create-brightness-val">100%</span>
            </div>
            <div class="speed-labels"><span>Sombre</span><span>Vif</span></div>
          </div>"""

if old_speed_group in c:
    c = c.replace(old_speed_group, new_speed_group)
    print("Brightness slider HTML OK")
else:
    print("Speed group NOT FOUND")

# 2. JS - lire brightness dans submitCreateScene
old_submit = """  var name = document.getElementById('create-name').value.trim();
  var speed = parseFloat(document.getElementById('create-speed').value);
  var colors = getActiveColors();"""

new_submit = """  var name = document.getElementById('create-name').value.trim();
  var speed = parseFloat(document.getElementById('create-speed').value);
  var brightness = parseInt(document.getElementById('create-brightness').value) || 100;
  var colors = getActiveColors();"""

if old_submit in c:
    c = c.replace(old_submit, new_submit)
    print("Submit brightness read OK")
else:
    print("Submit NOT FOUND")

# 3. Passer brightness dans le body du fetch
old_body = "      body: JSON.stringify({name:name, colors:colors, speed:speed, image_file:image_file})"
new_body = "      body: JSON.stringify({name:name, colors:colors, speed:speed, brightness:brightness, image_file:image_file})"

if old_body in c:
    c = c.replace(old_body, new_body)
    print("Fetch body OK")
else:
    print("Fetch body NOT FOUND")

# 4. Stocker brightness dans knownScenes
old_push = "      knownScenes.push({name:name, colors:colors, mode:'dynamic_palette', speed:speed, custom:true});"
new_push = "      knownScenes.push({name:name, colors:colors, mode:'dynamic_palette', speed:speed, brightness:brightness, custom:true});"

if old_push in c:
    c = c.replace(old_push, new_push)
    print("knownScenes push OK")
else:
    print("knownScenes push NOT FOUND")

# 5. Reset form - remettre brightness à 100
old_reset = "  document.getElementById('create-speed').value='0.5';\n  document.getElementById('create-speed-val').textContent='0.50';"
new_reset = "  document.getElementById('create-speed').value='0.5';\n  document.getElementById('create-speed-val').textContent='0.50';\n  document.getElementById('create-brightness').value='100';\n  document.getElementById('create-brightness-val').textContent='100%';"

if old_reset in c:
    c = c.replace(old_reset, new_reset)
    print("Reset OK")
else:
    print("Reset NOT FOUND")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("brightness slider:", "create-brightness" in c)
