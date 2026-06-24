# fix_nav.py — aligne les headers de plan.html et groups.html sur le style lumieres.html

BASE = 'https://snapcast.theroyaldave.fr'

PRIMARY_CSS = '.btn.primary{background:#1d9e75;border-color:#1d9e75;color:#fff}'

def make_nav(active):
    pages = [
        ('/', 'ti-list', 'Vue liste'),
        ('/plan.html', 'ti-map-2', 'Plan'),
        ('/groups.html', 'ti-stack', 'Groupes'),
        ('/lumieres.html', 'ti-bulb', 'Lumieres'),
    ]
    out = ''
    for href, icon, title in pages:
        cls = 'btn primary' if href == active else 'btn'
        out += f'<a href="{BASE}{href}" class="{cls}" title="{title}" style="padding:8px 12px;font-size:16px"><i class="ti ti-{icon}"></i></a>'
    return out

def make_header(logo_icon, active):
    nav = make_nav(active)
    return f'''<header>
  <div class="header-inner">
  <div class="header-left">
    <i class="ti ti-{logo_icon} logo"></i>
    <h1>Snapcast</h1>
    <div class="status">
      <div class="status-dot" id="status-dot"></div>
      <span id="status-txt"></span>
    </div>
  </div>
  <div class="header-right">
    {nav}
    <button class="btn" onclick="location.reload()" title="Actualiser" style="padding:8px 12px;font-size:16px"><i class="ti ti-refresh"></i></button>
  </div>
  </div>
</header>'''

HEADER_CSS = '''header{background:#111;border-bottom:1px solid #222;flex-shrink:0}
.header-inner{display:flex;align-items:center;justify-content:space-between;padding:10px 20px;max-width:1200px;margin:0 auto;width:100%}
.header-left{display:flex;align-items:center;gap:12px}
.header-right{display:flex;align-items:center;gap:8px}
.btn{-webkit-appearance:none;appearance:none;background:#1a1a1a;border:1px solid #333;border-radius:8px;color:#ccc;cursor:pointer;font-size:12px;padding:6px 12px;display:flex;align-items:center;gap:5px;font-family:inherit;text-decoration:none}
.btn:hover{background:#222;border-color:#444}
.btn.primary{background:#1d9e75;border-color:#1d9e75;color:#fff}'''

import re

files = {
    'plan.html':   ('brand-spotify', '/plan.html'),
    'groups.html': ('stack', '/groups.html'),
}

for fname, (logo, active) in files.items():
    path = f'/var/www/snapcast-ui/{fname}'
    with open(path, 'r') as f:
        c = f.read()

    # Remplacer le bloc header CSS
    old_css_patterns = [
        r'header\{display:flex[^}]+\}',
        r'\.header-left\{[^}]+\}',
        r'\.header-right\{[^}]+\}',
        r'\.btn\{[^}]+\}',
        r'\.btn:hover\{[^}]+\}',
        r'\.btn\.primary\{[^}]+\}',
    ]
    # Supprimer les anciennes regles CSS header
    for pat in old_css_patterns:
        c = re.sub(pat, '', c)

    # Injecter le nouveau CSS apres </style> ouvrante ou avant </style>
    c = c.replace('</style>', HEADER_CSS + '\n</style>', 1)

    # Remplacer le bloc <header>...</header>
    new_header = make_header(logo, active)
    c = re.sub(r'<header>.*?</header>', new_header, c, flags=re.DOTALL)

    with open(path, 'w') as f:
        f.write(c)
    print(f'{fname}: OK')

print('Termine')
