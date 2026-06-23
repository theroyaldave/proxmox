import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS
preview_css = """
/* LAYOUT CREATE + PREVIEW */
.create-and-preview{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
@media(max-width:800px){.create-and-preview{grid-template-columns:1fr}}

/* PREVIEW PANEL */
.preview-panel{background:#111;border:1px solid #1e1e1e;border-radius:14px;padding:20px 24px;display:flex;flex-direction:column;gap:16px;min-height:340px}
.preview-panel-title{font-size:13px;font-weight:600;color:#e0e0e0;display:flex;align-items:center;gap:8px}
.preview-scene-name{font-size:11px;color:#5dcaa5;margin-left:auto;font-style:italic;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bulb-room{display:flex;align-items:flex-end;justify-content:center;gap:32px;flex:1;padding:20px 0}
.bulb-wrap{display:flex;flex-direction:column;align-items:center;gap:8px}
.bulb-label{font-size:10px;color:#555}
.bulb-svg{position:relative;width:70px;height:110px}
.bulb-glow{
  position:absolute;bottom:30px;left:50%;transform:translateX(-50%);
  width:90px;height:90px;border-radius:50%;
  filter:blur(22px);opacity:0.55;
  transition:background 1.5s ease, opacity 0.5s;
  pointer-events:none;
}
.bulb-off .bulb-glow{opacity:0}
.preview-info{font-size:11px;color:#444;text-align:center;padding-bottom:4px}
.preview-no-scene{font-size:12px;color:#333;text-align:center;margin:auto;font-style:italic}
"""
c = c.replace("</style>", preview_css + "\n</style>")

# 2. Wrapper la section create dans une grille create-and-preview
old_create_section = '<div class="create-section">'
new_create_section = '<div class="create-section"><div class="create-and-preview">'

c = c.replace(old_create_section, new_create_section, 1)

# Trouver la fin du create-panel et ajouter le preview panel + fermer la grille
old_create_end = """      <div class="create-actions">
        <span class="create-result" id="create-result"></span>
        <button class="btn" onclick="resetCreateForm()"><i class="ti ti-x"></i> Réinitialiser</button>
        <button class="btn primary" onclick="submitCreateScene()"><i class="ti ti-plus"></i> Créer le scénario</button>
      </div>
    </div>
  </div>
</main>"""

new_create_end = """      <div class="create-actions">
        <span class="create-result" id="create-result"></span>
        <button class="btn" onclick="resetCreateForm()"><i class="ti ti-x"></i> Réinitialiser</button>
        <button class="btn primary" onclick="submitCreateScene()"><i class="ti ti-plus"></i> Créer le scénario</button>
      </div>
    </div>
  </div>

  <!-- PREVIEW PANEL -->
  <div class="preview-panel" id="preview-panel">
    <div class="preview-panel-title">
      <i class="ti ti-bulb" style="color:#f5a623"></i> Aperçu lumineux
      <span class="preview-scene-name" id="preview-scene-label">Aucun scénario</span>
    </div>
    <div class="bulb-room" id="bulb-room">
      <div class="preview-no-scene" id="preview-no-scene">
        Cliquez sur un scénario<br>ou utilisez l'aperçu du formulaire
      </div>
    </div>
    <div class="preview-info" id="preview-info"></div>
  </div>

</div><!-- end create-and-preview -->
</main>"""

c = c.replace(old_create_end, new_create_end)

# 3. JS pour les ampoules
bulb_js = """
// ─── APERÇU AMPOULES ────────────────────────────────────────────
let previewColors = [];
let previewSpeed = 0.5;
let previewAnimFrame = null;
let previewColorIdx = [0, 1];
let previewT = [0, 0];
let previewLastTime = null;
const N_BULBS = 2;

function buildBulbs(colors) {
  const room = document.getElementById('bulb-room');
  const noScene = document.getElementById('preview-no-scene');
  if (!colors || !colors.length) {
    room.innerHTML = '<div class="preview-no-scene" id="preview-no-scene">Cliquez sur un scénario<br>ou utilisez l\\'aperçu du formulaire</div>';
    return;
  }
  if (noScene) noScene.remove();

  room.innerHTML = Array.from({length: N_BULBS}, (_, i) => `
    <div class="bulb-wrap">
      <div class="bulb-svg" id="bulb-svg-${i}">
        <div class="bulb-glow" id="bulb-glow-${i}"></div>
        <svg viewBox="0 0 70 110" xmlns="http://www.w3.org/2000/svg" width="70" height="110">
          <!-- Verre ampoule -->
          <ellipse cx="35" cy="38" rx="26" ry="30" fill="url(#bg${i})" opacity="0.92"/>
          <path d="M14 55 Q10 75 20 85 Q28 95 35 97 Q42 95 50 85 Q60 75 56 55 Z" fill="url(#bg${i})" opacity="0.85"/>
          <!-- Culot -->
          <rect x="22" y="95" width="26" height="6" rx="2" fill="#555"/>
          <rect x="24" y="100" width="22" height="5" rx="1" fill="#444"/>
          <rect x="26" y="104" width="18" height="4" rx="1" fill="#333"/>
          <!-- Reflet -->
          <ellipse cx="26" cy="28" rx="6" ry="9" fill="white" opacity="0.13"/>
          <defs>
            <radialGradient id="bg${i}" cx="50%" cy="40%" r="60%">
              <stop offset="0%" stop-color="white" stop-opacity="0.9" id="bg${i}-s0"/>
              <stop offset="100%" stop-color="white" stop-opacity="0.5" id="bg${i}-s1"/>
            </radialGradient>
          </defs>
        </svg>
      </div>
      <div class="bulb-label">Ampoule ${i+1}</div>
    </div>
  `).join('');
}

function setBulbColor(idx, color) {
  const glow = document.getElementById('bulb-glow-'+idx);
  const s0 = document.getElementById('bg'+idx+'-s0');
  const s1 = document.getElementById('bg'+idx+'-s1');
  if (glow) glow.style.background = color;
  if (s0) { s0.setAttribute('stop-color', color); s0.setAttribute('stop-opacity', '1'); }
  if (s1) { s1.setAttribute('stop-color', color); s1.setAttribute('stop-opacity', '0.6'); }
}

function hexToRgb(h) {
  h = h.replace('#','');
  return [parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16)];
}

function lerpColor(c1, c2, t) {
  const a = hexToRgb(c1), b = hexToRgb(c2);
  const r = Math.round(a[0] + (b[0]-a[0])*t);
  const g = Math.round(a[1] + (b[1]-a[1])*t);
  const bl = Math.round(a[2] + (b[2]-a[2])*t);
  return `rgb(${r},${g},${bl})`;
}

function animateBulbs(ts) {
  if (!previewLastTime) previewLastTime = ts;
  const dt = (ts - previewLastTime) / 1000;
  previewLastTime = ts;

  // Vitesse : speed 0→1 = cycle 12s→2s
  const cycleDuration = 12 - previewSpeed * 10;

  for (let i = 0; i < N_BULBS; i++) {
    previewT[i] += dt / cycleDuration;
    if (previewT[i] >= 1) {
      previewT[i] = 0;
      previewColorIdx[i] = (previewColorIdx[i] + 1) % previewColors.length;
    }
    const nextIdx = (previewColorIdx[i] + 1) % previewColors.length;
    const color = lerpColor(previewColors[previewColorIdx[i]], previewColors[nextIdx], previewT[i]);
    setBulbColor(i, color);
  }

  previewAnimFrame = requestAnimationFrame(animateBulbs);
}

function startPreview(colors, speed, sceneName) {
  if (previewAnimFrame) cancelAnimationFrame(previewAnimFrame);
  previewLastTime = null;
  previewColors = colors && colors.length ? colors : ['#ffffff'];
  previewSpeed = speed !== undefined ? speed : 0.5;
  // Décaler les ampoules
  previewColorIdx = [0, Math.floor(previewColors.length / 2)];
  previewT = [0, 0];
  buildBulbs(previewColors);
  document.getElementById('preview-scene-label').textContent = sceneName || 'Aperçu';
  const info = document.getElementById('preview-info');
  if (info) info.textContent = previewColors.length + ' couleur(s) — vitesse ' + previewSpeed.toFixed(2);
  previewAnimFrame = requestAnimationFrame(animateBulbs);
}

function stopPreview() {
  if (previewAnimFrame) { cancelAnimationFrame(previewAnimFrame); previewAnimFrame = null; }
}
// ─── FIN APERÇU ──────────────────────────────────────────────────
"""

# Insérer avant initColorPickers
c = c.replace(
    "function initColorPickers()",
    bulb_js + "\nfunction initColorPickers()"
)

# 4. Cliquer sur une carte scénario → lancer aperçu
old_card_onclick = "onclick=\"selectScene('"
# Chercher la fonction selectScene ou le click sur la carte
# On ajoute l'appel startPreview dans renderSceneCard
old_card_div = 'const isCustom = !!scene.custom;\n  return `<div class="scene-card${isCustom?\' custom\':\'\'}"'
new_card_div = '''const isCustom = !!scene.custom;
  const cardColors = scene.colors || [];
  return `<div class="scene-card${isCustom?' custom':''}" onclick="startPreview(${JSON.stringify(cardColors)}, 0.5, '${scene.name.replace(/'/g,"\\\'")}')"'''

c = c.replace(old_card_div, new_card_div)

# 5. Bouton aperçu dans le formulaire — à côté de Réinitialiser
c = c.replace(
    '<button class="btn" onclick="resetCreateForm()"><i class="ti ti-x"></i> Réinitialiser</button>',
    '<button class="btn" onclick="resetCreateForm()"><i class="ti ti-x"></i> Réinitialiser</button>\n        <button class="btn" onclick="startPreview(getActiveColors(), parseFloat(document.getElementById(\'create-speed\').value), document.getElementById(\'create-name\').value||\'Aperçu\')"><i class="ti ti-eye"></i> Aperçu</button>'
)

# 6. Mise à jour aperçu en temps réel quand on change les couleurs ou la vitesse
c = c.replace(
    "function updatePreviewDots() {",
    """function updatePreviewDots() {
  // Mise à jour aperçu si actif
  if (previewAnimFrame) {
    const colors = getActiveColors();
    const speed = parseFloat(document.getElementById('create-speed').value);
    startPreview(colors, speed, document.getElementById('create-name').value||'Aperçu');
  }"""
)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

checks = [
    ('preview-panel' in c, 'preview panel HTML'),
    ('bulb-glow' in c, 'bulb glow'),
    ('startPreview' in c, 'startPreview JS'),
    ('animateBulbs' in c, 'animateBulbs'),
    ('lerpColor' in c, 'lerpColor'),
    ('create-and-preview' in c, 'grid layout'),
    ('Aperçu' in c, 'bouton aperçu'),
]
for ok, name in checks:
    print(f"{'✓' if ok else '✗'} {name}")
