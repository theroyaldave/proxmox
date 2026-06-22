#!/usr/bin/env python3
# patch_hue_index.py — ajoute le bouton 💡 Hue dans index.html

content = open('/var/www/snapcast-ui/index.html').read()

# 1. Ajouter GROUP_HUE_ROOM après GROUP_IMAGE
old_group_image = '''const GROUP_NS300={
  "4310351e-aa93-5793-7707-dd021425830b":true,
};'''

new_group_image = '''const GROUP_NS300={
  "4310351e-aa93-5793-7707-dd021425830b":true,
};
// Mapping groupId → room_id Hue v2
const GROUP_HUE_ROOM={
  "ca134b93-8951-9f02-b5fd-b5060d5458f0":"2c0ad668-c4d4-4d9b-95da-2cebc9142c33", // Atelier
  "016e3537-578f-b2cd-5a37-48ebc1d5a8ea":"58b32637-7212-4f10-b62c-2b19e987acc2", // SDJ
  "3fa5da3f-8ba3-df55-feb8-c801659364f4":"1e9b2c5d-4adc-48f8-86be-754fd33ba6ba", // Cuisine
  "4310351e-aa93-5793-7707-dd021425830b":"5960401e-b642-4d78-a0db-a505f6c03a35", // Parents
  "6eb0e7b9-39fe-67ee-4707-2a121c6e111b":"dd1e3e36-c9a1-4ed0-89c8-79d5e6119502", // Lilian
  "fce87803-8613-471a-218e-a83250f02558":"c68e49c4-aded-4a29-aa6a-4c189c282c09", // Thaïs
};'''

content = content.replace(old_group_image, new_group_image)

# 2. Ajouter variables état Hue après les déclarations d'état existantes
old_state = "let rebootState={};"
new_state = """let rebootState={};
let hueActive={};       // groupId → true/false
let hueSnapshot={};     // groupId → snapshot état lumières avant activation
let hueConfig=null;     // contenu de hue-config.json
let nowPlayingFeatures={}; // contenu de now-playing-features.json
let hueLastTrack={};    // groupId → dernière piste traitée"""

content = content.replace(old_state, new_state)

# 3. Ajouter fetchNowPlayingFeatures et fetchHueConfig après fetchNowPlaying
old_fetch = "async function snapclientControl"
new_fetch = """async function fetchNowPlayingFeatures(){
  try{const r=await fetch('/now-playing-features.json?_='+Date.now());nowPlayingFeatures=await r.json();}catch(e){nowPlayingFeatures={};}
}
async function fetchHueConfig(){
  if(hueConfig)return;
  try{const r=await fetch('/hue-config.json?_='+Date.now());hueConfig=await r.json();}catch(e){}
}
function getHueStyle(streamId){
  const f=nowPlayingFeatures[streamId];
  return f?f.style||'defaut':'defaut';
}
function getHueSceneForStyle(roomName,styleId){
  if(!hueConfig)return'Lumineux';
  const room=Object.entries(hueConfig.rooms).find(([n])=>n===roomName);
  const style=hueConfig.styles.find(s=>s.id===styleId);
  if(!style)return'Lumineux';
  const scenes=(room&&room[1].scenes&&room[1].scenes[styleId])?room[1].scenes[styleId]:style.scenes;
  const valid=scenes.filter(s=>s&&s.length>0);
  if(!valid.length)return'Lumineux';
  return valid[Math.floor(Math.random()*valid.length)];
}
function getRoomNameForGroup(groupId){
  const label=GROUPS[groupId]?GROUPS[groupId].label:'';
  return label;
}
async function activateHue(groupId){
  const roomId=GROUP_HUE_ROOM[groupId];
  if(!roomId)return;
  await fetchHueConfig();
  // Snapshot état actuel
  try{
    const r=await fetch('/hue-get-state?room_id='+roomId);
    const snap=await r.json();
    hueSnapshot[groupId]=snap;
  }catch(e){hueSnapshot[groupId]={};}
  hueActive[groupId]=true;
  hueLastTrack[groupId]='';
  renderGroups();
  await triggerHueScene(groupId);
}
async function deactivateHue(groupId){
  hueActive[groupId]=false;
  renderGroups();
  const snap=hueSnapshot[groupId];
  if(!snap)return;
  try{
    await fetch('/hue-restore-state',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        grouped_light_id:snap.light_state?snap.light_state.grouped_light_id:'',
        light_state:snap.light_state||{},
        active_scene_id:snap.active_scene_id||null
      })
    });
  }catch(e){}
  delete hueSnapshot[groupId];
  delete hueLastTrack[groupId];
}
async function triggerHueScene(groupId){
  const roomId=GROUP_HUE_ROOM[groupId];
  if(!roomId||!hueActive[groupId])return;
  const s=state[groupId]||{};
  const streamId=s.stream||'';
  const styleId=getHueStyle(streamId);
  const roomName=getRoomNameForGroup(groupId);
  const sceneName=getHueSceneForStyle(roomName,styleId);
  try{
    await fetch('/activate-hue-scene',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({room_id:roomId,scene_name:sceneName})
    });
  }catch(e){}
}
async function hueAutoUpdate(){
  for(const groupId of Object.keys(hueActive)){
    if(!hueActive[groupId])continue;
    const s=state[groupId]||{};
    const streamId=s.stream||'';
    const np=nowPlaying[streamId];
    const trackKey=np?(np.track+'|'+np.artist):'';
    if(trackKey&&trackKey!==hueLastTrack[groupId]){
      hueLastTrack[groupId]=trackKey;
      await triggerHueScene(groupId);
    }
  }
}
async function snapclientControl"""

content = content.replace(old_fetch, new_fetch)

# 4. Ajouter le bouton 💡 dans la carte enceinte (après rebootBtn)
old_card_header = """+'<div style="display:flex;align-items:center;gap:6px">'+rebootBtn+'<span style="font-size:11px;padding:2px 7px;border-radius:20px;background:'+badgeBg+';color:'+badgeColor+';border:1px solid '+badgeBorder+'">'+badgeText+'</span></div>'"""

new_card_header = """+'<div style="display:flex;align-items:center;gap:6px">'+rebootBtn+(GROUP_HUE_ROOM[id]?(function(){const hOn=hueActive[id];const canHue=isActive&&!muted;return '<button onclick="'+(hOn?'deactivateHue':'activateHue')+'(\\''+id+'\\')" title="'+(hOn?'Désactiver lumières':'Activer lumières Hue')+'" style="-webkit-appearance:none;-moz-appearance:none;appearance:none;background:'+(hOn?'rgba(245,166,35,0.15)':'none')+';border:'+(hOn?'1px solid #f5a623':'none')+';border-radius:6px;cursor:'+(canHue?'pointer':'not-allowed')+';padding:3px 5px;color:'+(hOn?'#f5a623':(canHue?'#888':'#333'))+';display:flex;align-items:center;opacity:'+(canHue||hOn?1:0.4)+'"><i class="ti ti-bulb" style="font-size:15px"></i></button>';}()):'')+'<span style="font-size:11px;padding:2px 7px;border-radius:20px;background:'+badgeBg+';color:'+badgeColor+';border:1px solid '+badgeBorder+'">'+badgeText+'</span></div>'"""

content = content.replace(old_card_header, new_card_header)

# 5. Ajouter hueAutoUpdate + fetchNowPlayingFeatures dans refresh()
old_auto_join = "autoJoinStreams();\n}"
new_auto_join = """autoJoinStreams();
  fetchNowPlayingFeatures().then(hueAutoUpdate);
}"""

content = content.replace(old_auto_join, new_auto_join)

# 6. Ajouter lien Lumières dans le header (après le lien Groupes)
old_links = '''<a href="https://snapcast.theroyaldave.fr/groups.html" style="text-decoration:none;background:#1a1a1a;border:1px solid #444;border-radius:8px;color:#fff;padding:6px 10px;cursor:pointer;display:flex;align-items:center;gap:6px;font-size:13px"><i class="ti ti-stack"></i> Groupes</a>'''
new_links = old_links + '''<a href="/lumieres.html" style="text-decoration:none;background:#1a1a1a;border:1px solid #444;border-radius:8px;color:#f5a623;padding:6px 10px;cursor:pointer;display:flex;align-items:center;gap:6px;font-size:13px"><i class="ti ti-bulb"></i> Lumières</a>'''
content = content.replace(old_links, new_links)

# 7. Appel initial fetchHueConfig
old_init = "refresh();\nsetInterval(refresh,10000);"
new_init = """fetchHueConfig();
refresh();
setInterval(refresh,10000);"""

content = content.replace(old_init, new_init)

open('/var/www/snapcast-ui/index.html', 'w').write(content)

checks = ['GROUP_HUE_ROOM', 'activateHue', 'deactivateHue', 'triggerHueScene', 'hueAutoUpdate', 'ti-bulb', 'lumieres.html']
for c in checks:
    print(f"{'OK' if c in content else 'MISSING'}: {c}")
