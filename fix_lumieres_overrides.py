with open('/var/www/snapcast-ui/lumieres.html', 'r') as f:
    src = f.read()

import re

# Fix data-key avec apostrophes corrompues (pattern: data-key=''+escAttr(key)+'')
src = re.sub(
    r"data-key=''(\+escAttr\(key\)\+)''",
    r'data-key="+\1+"',
    src
)

# Fix toggleOvrDropdown data-key avec apostrophes corrompues
src = re.sub(
    r"(toggleOvrDropdown\(this,this\.dataset\.key\)\" )data-key=''(\+escAttr\(key\)\+)''",
    r'\1data-key="+\2+"',
    src
)

# Fix onmouseover/onmouseout corrompus
src = src.replace(
    "onmouseover=\"this.style.color=''#e55''\"",
    "onmouseover=\"this.style.color='#e55'\""
)
src = src.replace(
    "onmouseout=\"this.style.color=''#555''\"",
    "onmouseout=\"this.style.color='#555'\""
)

# Verifier le resultat
if 'data-key="+escAttr' in src:
    print('data-key OK')
else:
    print('ATTENTION: data-key pattern non trouve, verifier manuellement')

lines = src.splitlines()
print('done - lignes:', len(lines))

with open('/var/www/snapcast-ui/lumieres.html', 'w') as f:
    f.write(src)
