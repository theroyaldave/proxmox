import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. Dans renderSceneCard, remplacer le onclick inline JSON par data-attributes
old_card = '''const isCustom = !!scene.custom;
  const cardColors = scene.colors || [];
  return `<div class="scene-card${isCustom?' custom':''}" onclick="startPreview(${JSON.stringify(cardColors)}, 0.5, '${scene.name.replace(/'/g,"\\'")}')"'''

new_card = '''const isCustom = !!scene.custom;
  const cardColors = scene.colors || [];
  const safeColors = encodeURIComponent(JSON.stringify(cardColors));
  const safeName = scene.name.replace(/'/g,"\\'");
  return `<div class="scene-card${isCustom?' custom':''}" data-colors="${safeColors}" data-name="${scene.name.replace(/"/g,'&quot;')}" onclick="handleCardClick(this)"'''

c = c.replace(old_card, new_card)

# 2. Ajouter la fonction handleCardClick
handle_fn = """
function handleCardClick(el) {
  const colors = JSON.parse(decodeURIComponent(el.dataset.colors || '[]'));
  const name = el.dataset.name || '';
  const speed = 0.5;
  startPreview(colors, speed, name);
}
"""

c = c.replace(
    "function startPreview(",
    handle_fn + "\nfunction startPreview("
)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("handleCardClick:", "handleCardClick" in c)
print("data-colors:", "data-colors" in c)
print("encodeURIComponent:", "encodeURIComponent" in c)
