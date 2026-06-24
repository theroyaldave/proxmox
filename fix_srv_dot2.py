import re

with open("/var/www/snapcast-ui/index.html", "r") as f:
    c = f.read()

# 1. Supprimer TOUS les srv-dot existants
c = re.sub(r'<div id="srv-dot"[^>]*/>\s*', '', c)
c = re.sub(r'<div id=["\']srv-dot["\'][^>]*/>\s*', '', c)

# 2. Le remettre UNE SEULE FOIS avant le SVG Spotify dans le h1
# Mais cette fois AVANT le SVG (à gauche)
c = c.replace(
    '<h1>\n      <svg',
    '<h1><div id="srv-dot" style="width:8px;height:8px;border-radius:50%;background:#1db954;flex-shrink:0;display:inline-block;margin-right:8px;vertical-align:middle;transition:background .3s"></div><svg'
)

# 3. S'assurer que le JS qui met à jour srv-dot fonctionne toujours
print("srv-dot count:", c.count('id="srv-dot"'))

with open("/var/www/snapcast-ui/index.html", "w") as f:
    f.write(c)
