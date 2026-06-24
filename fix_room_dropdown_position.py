with open("/var/www/snapcast-ui/lumieres.html", "r") as f:
    c = f.read()

# CSS - dropdown dans le body
old_css = """.scene-room-dropdown{
  position:absolute;top:32px;left:7px;
  background:#1a1a1a;border:1px solid #333;border-radius:10px;
  z-index:300;min-width:160px;
  box-shadow:0 8px 24px rgba(0,0,0,.7);
  overflow:hidden;
}"""

new_css = """.scene-room-dropdown{
  position:fixed;
  background:#1a1a1a;border:1px solid #333;border-radius:10px;
  z-index:9999;min-width:160px;
  box-shadow:0 8px 24px rgba(0,0,0,.7);
  overflow:hidden;
}"""

if old_css in c:
    c = c.replace(old_css, new_css)
    print("CSS fixed OK")
else:
    print("CSS NOT FOUND")

# JS - positionner le dropdown par rapport au bouton
old_fn = """  var dropdown = document.createElement('div');
  dropdown.className = 'scene-room-dropdown';
  dropdown.innerHTML = '<div class="scene-room-dropdown-title">Activer dans</div>'
    + rooms.map(function([rn, rc]) {
        return '<div class="scene-room-dropdown-item" onclick="activateSceneInRoom(event,\\''+rn+'\\',\\''+rc.hue_room_id+'\\',\\''+sceneName.replace(/'/g,"\\\\'")+'\\')">'
          +'<span>'+rn+'</span>'
          +'</div>';
      }).join('');

  btn.appendChild(dropdown);"""

new_fn = """  var rect = btn.getBoundingClientRect();
  var dropdown = document.createElement('div');
  dropdown.className = 'scene-room-dropdown';
  dropdown.style.top = (rect.bottom + 4) + 'px';
  dropdown.style.left = rect.left + 'px';
  dropdown.innerHTML = '<div class="scene-room-dropdown-title">Activer dans</div>'
    + rooms.map(function([rn, rc]) {
        return '<div class="scene-room-dropdown-item" onclick="activateSceneInRoom(event,\\''+rn+'\\',\\''+rc.hue_room_id+'\\',\\''+sceneName.replace(/'/g,"\\\\'")+'\\')">'
          +'<span>'+rn+'</span>'
          +'</div>';
      }).join('');

  document.body.appendChild(dropdown);"""

if old_fn in c:
    c = c.replace(old_fn, new_fn)
    print("Dropdown position OK")
else:
    print("Dropdown fn NOT FOUND")

# Fermer : remove de body au lieu de btn
old_remove = """        dropdown.remove();
        btn._menuOpen = false;
        document.removeEventListener('click', handler);"""

new_remove = """        if (dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
        btn._menuOpen = false;
        document.removeEventListener('click', handler);"""

if old_remove in c:
    c = c.replace(old_remove, new_remove)
    print("Remove fixed OK")
else:
    print("Remove NOT FOUND")

# Aussi dans activateSceneInRoom
old_remove2 = "        document.querySelectorAll('.scene-room-dropdown').forEach(function(d){ d.remove(); });"
new_remove2 = "        document.querySelectorAll('.scene-room-dropdown').forEach(function(d){ if(d.parentNode) d.parentNode.removeChild(d); });"

c = c.replace(old_remove2, new_remove2)

with open("/var/www/snapcast-ui/lumieres.html", "w") as f:
    f.write(c)

print("position:fixed:", "position:fixed" in c)
print("getBoundingClientRect:", "getBoundingClientRect" in c)
