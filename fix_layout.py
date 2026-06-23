import re

with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. Cacher le footer sticky
c = c.replace(
    ".footer-bar{position:sticky;bottom:0;background:#111;border-top:1px solid #222;padding:12px 20px;display:flex;align-items:center;justify-content:space-between}",
    ".footer-bar{display:none!important}"
)

# 2. Ajouter CSS rooms-actions avant </style>
rooms_css = """
.rooms-actions{display:flex;align-items:center;justify-content:space-between;padding:12px 0 16px}
.rooms-actions-right{display:flex;gap:8px}
.rooms-footer-info{font-size:12px;color:#555}
.rooms-footer-info.modified{color:#5dcaa5}
"""
c = c.replace("</style>", rooms_css + "\n</style>")

# 3. Injecter le bloc boutons juste après le titre "Configuration par pièce"
rooms_actions_html = """
    <div class="rooms-actions">
      <span class="rooms-footer-info" id="footer-info">Aucune modification</span>
      <div class="rooms-actions-right">
        <button class="btn" onclick="cancelChanges()"><i class="ti ti-x"></i> Annuler</button>
        <button class="btn primary" onclick="showSaveModal()"><i class="ti ti-device-floppy"></i> Sauvegarder</button>
      </div>
    </div>"""

c = re.sub(
    r'(<div class="section-title">Configuration par pi[^<]+</div>)',
    r'\1' + rooms_actions_html,
    c
)

# 4. Corriger le label doublon dans le formulaire
c = re.sub(r'Couleurs \(jusqu.*?\) [—-] 9 couleurs de la palette', '9 couleurs de la palette', c, flags=re.IGNORECASE)
c = re.sub(r'COULEURS \(JUSQU.*?\) [—-] 9 COULEURS DE LA PALETTE', '9 COULEURS DE LA PALETTE', c, flags=re.IGNORECASE)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

# Vérifs
print("footer hidden:", "display:none!important" in c)
print("rooms-actions:", "rooms-actions" in c)
print("footer-info inline:", c.count('id="footer-info"'))
