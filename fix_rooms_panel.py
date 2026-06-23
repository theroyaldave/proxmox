import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. CSS panel
panel_css = """
.rooms-panel{background:#111;border:1px solid #1e1e1e;border-radius:12px;overflow:hidden}
.rooms-panel .room-card{border-left:none;border-right:none;border-radius:0}
.rooms-panel .room-card:first-child{border-top:none}
.rooms-panel-footer{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-top:1px solid #1e1e1e;background:#0d0d0d}
"""
c = c.replace("</style>", panel_css + "\n</style>")

# 2. Supprimer l'ancien bloc rooms-actions au-dessus
c = re.sub(r'\s*<div class="rooms-actions">.*?</div>\s*', '\n    ', c, flags=re.DOTALL, count=1)

# 3. Supprimer l'ancienne mise a jour footer-info dans render()
c = c.replace(
    "  const info = document.getElementById('footer-info');\n  info.textContent = modified ? 'Modifications non sauvegardées' : 'Aucune modification';\n  info.className = 'footer-info' + (modified ? ' modified' : '');",
    "  // footer-info gere dans rooms-panel-footer"
)

# 4. Wrapper HTML rooms-list dans un panel
c = c.replace(
    '<div id="rooms-list" class="rooms-list">',
    '<div class="rooms-panel"><div id="rooms-list" class="rooms-list">'
)

# 5. Injecter footer apres loadCustomScenes/render
c = c.replace(
    "    await loadCustomScenes();\n    render();",
    """    await loadCustomScenes();
    render();
    if (!document.getElementById('rooms-panel-footer')) {
      const panel = document.querySelector('.rooms-panel');
      if (panel) {
        const footer = document.createElement('div');
        footer.id = 'rooms-panel-footer';
        footer.className = 'rooms-panel-footer';
        footer.innerHTML = '<span class="rooms-footer-info" id="footer-info">Aucune modification</span>'
          + '<div style="display:flex;gap:8px">'
          + '<button class="btn" onclick="cancelChanges()"><i class="ti ti-x"></i> Annuler</button>'
          + '<button class="btn primary" onclick="showSaveModal()"><i class="ti ti-device-floppy"></i> Sauvegarder</button>'
          + '</div>';
        panel.appendChild(footer);
      }
    }"""
)

# 6. Mettre a jour footer-info dans render() via rooms-panel-footer
c = re.sub(
    r"(  document\.getElementById\('rooms-list'\)\.innerHTML =.*?\.join\(''\);)",
    r"""\1
  const _fi = document.getElementById('footer-info');
  if (_fi) {
    _fi.textContent = modified ? 'Modifications non sauvegardées' : 'Aucune modification';
    _fi.className = 'rooms-footer-info' + (modified ? ' modified' : '');
  }""",
    c, flags=re.DOTALL
)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("rooms-panel css:", ".rooms-panel{" in c)
print("rooms-panel-footer css:", "rooms-panel-footer{" in c)
print("rooms-panel div:", 'class="rooms-panel"' in c)
print("footer-info count:", c.count('id="footer-info"'))
