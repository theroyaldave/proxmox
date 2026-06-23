with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# Modifier le message de succès après création
old_msg = """      const nb = data.created ? data.created.length : 0;
      resultEl.textContent = `✓ "${name}" créé dans ${nb} pièce(s)` + (data.errors&&data.errors.length?` — ${data.errors.length} erreur(s)`:'');
      resultEl.className = 'create-result ok';"""

new_msg = """      resultEl.textContent = '✓ "' + name + '" sauvegardé localement — assignez-le à un style puis cliquez Sauvegarder pour l\\'envoyer sur le bridge.';
      resultEl.className = 'create-result ok';"""

if old_msg in c:
    c = c.replace(old_msg, new_msg)
    print("message OK")
else:
    print("NOT FOUND - trying variant")
    import re
    c = re.sub(
        r"const nb = data\.created.*?resultEl\.className = 'create-result ok';",
        "resultEl.textContent = '✓ \"' + name + '\" sauvegardé localement — assignez-le à un style puis cliquez Sauvegarder.';\n      resultEl.className = 'create-result ok';",
        c, flags=re.DOTALL
    )
    print("regex applied")

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("sauvegarde localement:", "sauvegardé localement" in c)
