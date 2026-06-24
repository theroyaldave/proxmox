import re

NAV = '<a href="https://snapcast.theroyaldave.fr/" class="btn{0}" title="Vue liste" style="padding:8px 12px;font-size:16px"><i class="ti ti-list"></i></a><a href="https://snapcast.theroyaldave.fr/plan.html" class="btn{1}" title="Plan" style="padding:8px 12px;font-size:16px"><i class="ti ti-map-2"></i></a><a href="https://snapcast.theroyaldave.fr/groups.html" class="btn{2}" title="Groupes" style="padding:8px 12px;font-size:16px"><i class="ti ti-stack"></i></a><a href="https://snapcast.theroyaldave.fr/lumieres.html" class="btn{3}" title="Lumieres" style="padding:8px 12px;font-size:16px"><i class="ti ti-bulb"></i></a>'

PRIMARY_CSS = '.btn.primary{background:#1d9e75;border-color:#1d9e75;color:#fff}'

pages = {
    'index.html':    (' primary', '', '', ''),
    'plan.html':     ('', ' primary', '', ''),
    'groups.html':   ('', '', ' primary', ''),
    'lumieres.html': ('', '', '', ' primary'),
}

patterns = [
    re.compile(r'<a href="https?://snapcast\.theroyaldave\.fr/plan\.html"[^>]*>.*?ti-map.*?</a>.{0,200}?<a href="[^"]*lumieres\.html"[^>]*>.*?ti-bulb.*?</a>', re.DOTALL),
    re.compile(r'<a href="[^"]*" class="btn"[^>]*>.*?ti-list.*?</a>.{0,300}?<a href="[^"]*" class="btn"[^>]*>.*?ti-map.*?</a>', re.DOTALL),
    re.compile(r'<a href="https?://snapcast\.theroyaldave\.fr/"[^>]*>.*?ti-list.*?</a>.{0,200}?<a href="[^"]*lumieres\.html"[^>]*>.*?ti-bulb.*?</a>', re.DOTALL),
]

for fname, active in pages.items():
    path = f'/var/www/snapcast-ui/{fname}'
    try:
        with open(path, 'r') as f:
            c = f.read()
    except:
        print(f'{fname}: fichier introuvable')
        continue

    nav = NAV.format(*active)
    replaced = False

    for i, pat in enumerate(patterns):
        new_c, n = pat.subn(nav, c)
        if n > 0:
            c = new_c
            replaced = True
            print(f'{fname}: nav OK (pattern {i})')
            break

    if not replaced:
        print(f'{fname}: pattern non trouve')

    if '.btn.primary' not in c and '.btn{' in c:
        c = c.replace('.btn:hover{', PRIMARY_CSS + '.btn:hover{')
        print(f'{fname}: primary CSS ajoute')

    with open(path, 'w') as f:
        f.write(c)

print('Termine')
