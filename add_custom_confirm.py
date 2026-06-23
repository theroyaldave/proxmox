with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# 1. Ajouter showConfirm
confirm_fn = """
function showConfirm(msg) {
  return new Promise(function(resolve) {
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:9999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)';
    overlay.innerHTML = '<div style="background:#1a1a1a;border:1px solid #333;border-radius:14px;padding:28px 32px;max-width:380px;width:90%;text-align:center">'
      +'<div style="font-size:14px;color:#e0e0e0;margin-bottom:24px;line-height:1.5">'+msg+'</div>'
      +'<div style="display:flex;gap:10px;justify-content:center">'
      +'<button id="confirm-cancel" style="background:#222;border:1px solid #333;border-radius:8px;color:#aaa;padding:8px 20px;cursor:pointer;font-size:12px">Annuler</button>'
      +'<button id="confirm-ok" style="background:#c0392b;border:none;border-radius:8px;color:#fff;padding:8px 20px;cursor:pointer;font-size:12px;font-weight:600">Supprimer</button>'
      +'</div></div>';
    document.body.appendChild(overlay);
    overlay.querySelector('#confirm-ok').onclick = function() { document.body.removeChild(overlay); resolve(true); };
    overlay.querySelector('#confirm-cancel').onclick = function() { document.body.removeChild(overlay); resolve(false); };
  });
}
"""

c = c.replace("// \u2500\u2500\u2500 GESTIONNAIRE SC\u00c8NES PAR PI\u00c8CE", confirm_fn + "\n// \u2500\u2500\u2500 GESTIONNAIRE SC\u00c8NES PAR PI\u00c8CE")

# 2. Remplacer confirm natif par showConfirm
c = c.replace(
    "if (!confirm('Supprimer \"'+sceneName+'\" de '+roomName+' ?')) return;",
    "if (!(await showConfirm('Supprimer \"'+sceneName+'\" de '+roomName+' ?'))) return;"
)

# 3. Aussi remplacer le confirm dans deleteCustomScene
c = c.replace(
    "if (!confirm('Supprimer le sc\u00e9nario \"'+name+'\" ?')) return;",
    "if (!(await showConfirm('Supprimer le sc\u00e9nario \"'+name+'\" ?'))) return;"
)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("showConfirm:", "function showConfirm" in c)
print("await showConfirm deleteRoom:", "await showConfirm('Supprimer" in c)
