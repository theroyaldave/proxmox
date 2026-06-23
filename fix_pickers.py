import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

c = re.sub(
    r'function initColorPickers\(\).*?function updatePreviewDots',
    'function initColorPickers() {\n'
    '  const grid = document.getElementById("colors-grid");\n'
    '  if (!grid) return;\n'
    '  grid.innerHTML = "";\n'
    '  const defaults = ["#ff3c0a","#ff8023","#ffba09","#1affff","#3ce1ff","#a020f0","#00c864","#ff1493","#ffffff"];\n'
    '  for (let i = 0; i < 9; i++) {\n'
    '    const slot = document.createElement("div");\n'
    '    slot.className = "color-slot";\n'
    '    slot.innerHTML = "<span class=\\"color-slot-label\\">"+(i+1)+"</span>"\n'
    '      + "<div class=\\"color-picker-wrap\\" id=\\"cpwrap-"+i+"\\">"\n'
    '      + "<input type=\\"color\\" id=\\"cp-"+i+"\\" value=\\""+defaults[i]+"\\""\n'
    '      + " oninput=\\"updatePreviewDots()\\" onchange=\\"updatePreviewDots()\\"></div>";\n'
    '    grid.appendChild(slot);\n'
    '  }\n'
    '  updatePreviewDots();\n'
    '}\n'
    '\n'
    'function getActiveColors() {\n'
    '  return Array.from({length:9}, function(_,i){ return document.getElementById("cp-"+i).value; });\n'
    '}\n'
    '\n'
    'function updatePreviewDots',
    c, flags=re.DOTALL
)

c = c.replace("LES 1 \u00c0 5 SONT OBLIGATOIRES", "9 COULEURS DE LA PALETTE")
c = c.replace("les 1 \u00e0 5 sont obligatoires", "9 couleurs de la palette")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)
print("OK")
