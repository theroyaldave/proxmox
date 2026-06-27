import re

with open('/var/www/snapcast-ui/lumieres.html', 'r') as f:
    src = f.read()

old_render = re.search(r'function renderOverrides\(\)\{.*?^\}', src, re.DOTALL | re.MULTILINE)
if old_render:
    print('renderOverrides trouve, remplacement...')
else:
    print('renderOverrides NON TROUVE')

new_render = """function renderOverrides(){
  var list=document.getElementById('overrides-list');
  var count=document.getElementById('overrides-count');
  var keys=Object.keys(styleOverridesData);
  count.textContent=keys.length?'('+keys.length+')':'';
  list.innerHTML='';
  if(!keys.length){
    var empty=document.createElement('div');
    empty.style.cssText='color:#444;font-size:12px;padding:8px 0';
    empty.textContent='Aucune exception definie';
    list.appendChild(empty);
    return;
  }
  keys.forEach(function(key){
    var parts=key.split('|||');
    var artist=parts[0]||'';
    var track=parts[1]||'';
    var style=styleOverridesData[key];
    var label=STYLE_LABELS_OVR[style]||style;

    var row=document.createElement('div');
    row.style.cssText='display:flex;align-items:center;gap:10px;padding:8px 12px;background:#151515;border:1px solid #222;border-radius:8px;font-size:12px';

    var info=document.createElement('div');
    info.style.cssText='flex:1;min-width:0';
    var trackEl=document.createElement('div');
    trackEl.style.cssText='color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500';
    trackEl.textContent=track;
    var artistEl=document.createElement('div');
    artistEl.style.cssText='color:#666;font-size:11px;margin-top:2px';
    artistEl.textContent=artist;
    info.appendChild(trackEl);
    info.appendChild(artistEl);

    var badgeWrap=document.createElement('div');
    badgeWrap.style.cssText='position:relative';
    var badge=document.createElement('span');
    badge.style.cssText='cursor:pointer;padding:3px 10px;border-radius:10px;background:rgba(255,255,255,0.07);color:#5dcaa5;font-size:11px;display:inline-flex;align-items:center;gap:4px;user-select:none';
    badge.textContent=label+' \u25bc';
    badge.addEventListener('click', (function(k){ return function(){ toggleOvrDropdown(badge, k); }; })(key));
    badgeWrap.appendChild(badge);

    var btn=document.createElement('button');
    btn.title='Supprimer';
    btn.style.cssText='background:none;border:none;cursor:pointer;color:#555;padding:4px;display:flex;align-items:center;font-size:14px';
    btn.innerHTML='<i class="ti ti-trash"></i>';
    btn.addEventListener('mouseenter', function(){ btn.style.color='#e55'; });
    btn.addEventListener('mouseleave', function(){ btn.style.color='#555'; });
    btn.addEventListener('click', (function(k){ return function(){ deleteOverride(k); }; })(key));

    row.appendChild(info);
    row.appendChild(badgeWrap);
    row.appendChild(btn);
    list.appendChild(row);
  });
}"""

if old_render:
    src = src[:old_render.start()] + new_render + src[old_render.end():]
    print('remplacement OK')

# Fix toggleOvrDropdown : le premier argument est maintenant l'element badge directement
old_toggle = "function toggleOvrDropdown(el, key){"
new_toggle_start = "function toggleOvrDropdown(el, key){"
# La fonction utilise deja el comme element, c'est OK

with open('/var/www/snapcast-ui/lumieres.html', 'w') as f:
    f.write(src)
print('done - lignes:', len(src.splitlines()))
