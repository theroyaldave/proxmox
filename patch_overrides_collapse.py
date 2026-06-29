import re

with open('/var/www/snapcast-ui/lumieres.html', 'r') as f:
    content = f.read()

old = '''  <div class="section" id="overrides-section" style="margin-top:32px">
    <div class="section-title">Exceptions de style <span id="overrides-count" style="color:#444;font-size:10px"></span></div>
    <div id="overrides-list" style="display:flex;flex-direction:column;gap:6px">
      <div style="color:#444;font-size:12px">Chargement...</div>
    </div>
  </div>'''

new = '''  <div class="section" id="overrides-section" style="margin-top:32px">
    <div class="section-title" onclick="toggleOverrides()" style="cursor:pointer;display:flex;align-items:center;gap:8px;user-select:none">
      <span>Exceptions de style</span>
      <span id="overrides-count" style="color:#444;font-size:10px"></span>
      <span id="overrides-chevron" style="color:#444;font-size:12px;margin-left:auto;transition:transform .2s">▼</span>
    </div>
    <div id="overrides-list" style="display:none;flex-direction:column;gap:6px">
      <div style="color:#444;font-size:12px">Chargement...</div>
    </div>
  </div>'''

if old in content:
    content = content.replace(old, new)
    print("OK - section repliable ajoutée")
else:
    print("ERREUR - pattern non trouvé")
    exit(1)

# Ajouter la fonction toggleOverrides avant la fermeture du script
toggle_fn = '''
function toggleOverrides(){
  var list = document.getElementById('overrides-list');
  var chevron = document.getElementById('overrides-chevron');
  var visible = list.style.display !== 'none';
  list.style.display = visible ? 'none' : 'flex';
  chevron.style.transform = visible ? '' : 'rotate(180deg)';
}
'''

# Insérer avant renderOverrides
content = content.replace('function renderOverrides(){', toggle_fn + 'function renderOverrides(){', 1)

with open('/var/www/snapcast-ui/lumieres.html', 'w') as f:
    f.write(content)

print("OK - fonction toggleOverrides ajoutée")
