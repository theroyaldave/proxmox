import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS : preview-info plus visible + scene thumb dans le titre
css_add = """
.preview-info{font-size:13px;color:#ccc;text-align:center;padding-bottom:4px;font-weight:500}
.preview-scene-thumb{width:48px;height:32px;border-radius:6px;object-fit:cover;flex-shrink:0;background:#222}
.preview-scene-thumb-grad{width:48px;height:32px;border-radius:6px;flex-shrink:0}
.preview-scene-label-wrap{display:flex;align-items:center;gap:6px;margin-left:auto}
.preview-scene-name{font-size:11px;color:#5dcaa5;font-style:italic;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:120px}
"""
c = c.replace("</style>", css_add + "\n</style>")

# 2. Modifier le HTML du preview-panel-title pour avoir un wrap avec thumb
c = c.replace(
    '<span class="preview-scene-name" id="preview-scene-label">Aucun scenario</span>',
    '<div class="preview-scene-label-wrap" id="preview-scene-label-wrap">'
    '<span class="preview-scene-name" id="preview-scene-label">Aucun scenario</span>'
    '</div>'
)

# 3. Dans startPreview, mettre à jour le thumb + nom
old_start = "  document.getElementById('preview-scene-label').textContent = sceneName || 'Aperçu';"
new_start = """  document.getElementById('preview-scene-label').textContent = sceneName || 'Aperçu';
  // Thumb du scénario
  const wrap = document.getElementById('preview-scene-label-wrap');
  if (wrap) {
    const imgUrl = sceneImageUrl(sceneName);
    const info = getSceneInfo(sceneName);
    let thumbHtml = '';
    if (imgUrl && imgUrl.indexOf('defaut.jpg') === -1) {
      thumbHtml = '<img class="preview-scene-thumb" src="'+imgUrl+'" onerror="this.style.display=\\'none\\'">';
    } else {
      const grad = colorGradient(info.colors);
      thumbHtml = '<div class="preview-scene-thumb-grad" style="background:'+grad+'"></div>';
    }
    wrap.innerHTML = thumbHtml + '<span class="preview-scene-name" id="preview-scene-label">'+( sceneName || 'Aperçu')+'</span>';
  }"""

c = c.replace(old_start, new_start, 1)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("preview-info css:", ".preview-info{font-size:13px" in c)
print("thumb wrap:", "preview-scene-label-wrap" in c)
print("startPreview thumb:", "preview-scene-thumb" in c)
