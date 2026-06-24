import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. Supprimer les lignes dupliquées de room-active-scene (garder seulement la première)
pattern = r"(\s*\$\{isEnabled && roomCfg\._activeScene \? `<span class=\"room-active-scene\">\$\{roomCfg\._activeScene\}</span>` : ''\})"
matches = list(re.finditer(pattern, c))
print(f"room-active-scene occurrences: {len(matches)}")
if len(matches) > 1:
    for m in reversed(matches[1:]):
        c = c[:m.start()] + c[m.end():]
    print("Duplicates removed")

# 2. Voir ce qu'il y a autour de la ligne 1755 (_lightOn = true sans _activeScene)
lines = c.split('\n')
for i, line in enumerate(lines):
    if '_lightOn = true' in line:
        print(f"Line {i+1}: {line.strip()}")
        print(f"  Next: {lines[i+1].strip() if i+1 < len(lines) else 'EOF'}")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("Final room-active-scene count:", c.count("room-active-scene\">"))
