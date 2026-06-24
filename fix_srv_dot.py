import re

with open("/var/www/snapcast-ui/index.html", "r") as f:
    c = f.read()

# 1. Supprimer l'ancien srv-dot de son emplacement actuel
c = re.sub(r'<div id="srv-dot"[^>]*/>\s*', '', c)

# 2. Ajouter le srv-dot dans le h1 avant le SVG Spotify
c = c.replace(
    '<h1>\n      <svg',
    '<h1>\n      <div id="srv-dot" style="width:8px;height:8px;border-radius:50%;background:#1db954;flex-shrink:0;display:inline-block;margin-right:6px;vertical-align:middle;transition:background .3s"></div><svg'
)

with open("/var/www/snapcast-ui/index.html", "w") as f:
    f.write(c)

print("srv-dot in h1:", 'id="srv-dot"' in c)
