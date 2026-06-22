#!/usr/bin/env python3
# patch_plan_hue.py

content = open('/var/www/snapcast-ui/plan.html').read()

# 1. Ajouter GROUP_HUE_ROOM après GROUP_OWNTONE
old = "let state={},piStatus={},containerStatus={},streamStatus={},nowPlaying={},owntoneVolumes={},ns300Volumes={},spotifyVolumes={},playingStreams=[];"
new = """const GROUP_HUE_ROOM={
  "ca134b93-8951-9f02-b5fd-b5060d5458f0":"2c0ad668-c4d4-4d9b-95da-2cebc9142c33",
  "016e3537-578f-b2cd-5a37-48ebc1d5a8ea":"58b32637-7212-4f10-b62c-2b19e987acc2",
  "3fa5da3f-8ba3-df55-feb8-c801659364f4":"1e9b2c5d-4adc-48f8-86be-754fd33ba6ba",
  "4310351e-aa93-5793-7707-dd021425830b":"5960401e-b642-4d78-a0db-a505f6c03a35",
  "6eb0e7b9-39fe-67ee-4707-2a121c6e111b":"dd1e3e36-c9a1-4ed0-89c8-79d5e6119502",
  "fce87803-8613-471a-218e-a83250f02558":"c68e49c4-aded-4a29-aa6a-4c189c282c09",
};
const SCENE_IMAGE_MAP={
  "Aurore boréale":"Aurore_boreale.jpg","Champignon des bois":"Champignon_des_bois.jpg",
  "Chinatown":"Chinatown.jpg","Coucher de soleil sur la savane":"Coucher_de_soleil.jpg",
  "Détente":"Detente.jpg","Éclosion ambrée":"Eclosion_ambree.jpg",
  "Étang doré":"Etang_dore.jpg","Honolulu":"Honolulu.jpg","Ibiza":"Ibiza.jpg",
  "Lecture":"Lecture.jpg","Lumineux":"Lumineux.jpg","Magnéto":"Magneto.jpg",
  "Malibu pink":"Malibu_pink.jpg","Miami":"Miami.jpg","Rio":"Rio.jpg",
  "Rougegorge d'automne":"Rouge_gorge.jpg","Soho":"Soho.jpg","Sommeil":"Sommeil.jpg",
  "Starlight":"Starlight.jpg","Tokyo":"Tokyo.jpg","Ville de l'amour":"Ville_de_lamour.jpg",
  "Concentration":"Concentration.jpg","Veilleuse":"Veilleuse.jpg","Suzuka":"Suzuka.jpg"
};
let state={},piStatus={},containerStatus={},streamStatus={},nowPlaying={},owntoneVolumes={},ns300Volumes={},spotifyVolumes={},playingStreams=[];
let hueActive={},hueCurrentScene={},hueLastTrack={},hueLastStyle={},hueSnapshot={},hueStreamScene={},hueConfig=null,nowPlayingFeatures={};
try{
  const saved=JSON.parse(localStorage.getItem('hueState')||'{}');
  hueActive=saved.hueActive||{};
  hueCurrentScene=saved.hueCurrentScene||{};
  hueLastTrack=saved.hueLastTrack||{};
  hueSnapshot=saved.hueSnapshot||{};
  hueLastStyle=saved.hueLastStyle||{};
}catch(e){}
function saveHueState(){try{localStorage.setItem('hueState',JSON.stringify({hueActive,hueCurrentScene,hueLastTrack,hueSnapshot,hueLastStyle}));}catch(e){}}
async function fetchHueConfig(){if(hueConfig)return;try{const r=await fetch('/hue-config.json?_='+Date.now());hueConfig=await r.json();}catch(e){}}
async function fetchNowPlayingFeatures(){try{const r=await fetch('/now-playing-features.json?_='+Date.now());nowPlayingFeatures=await r.json();}catch(e){nowPlayingFeatures={};}}
function getHueStyle(streamId){const f=nowPlayingFeatures[streamId];return f?f.style||'defaut':'defaut';}
function getRoomNameForGroupPlan(groupId){const names={"ca134b93-8951-9f02-b5fd-b5060d5458f0":"Atelier (enceinte)","016e3537-578f-b2cd-5a37-48ebc1d5a8ea":"Salle de jeux (enceinte)","3fa5da3f-8ba3-df55-feb8-c801659364f4":"Cuisine (enceinte)","4310351e-aa93-5793-7707-dd021425830b":"Chambre Parents (enceinte)","6eb0e7b9-39fe-67ee-4707-2a121c6e111b":"Chambre Lilian (enceinte)","fce87803-8613-471a-218e-a83250f02558":"Chambre Thaïs (rpi)"};return names[groupId]||'';}
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
async function activateHue(groupId){
  const roomId=GROUP_HUE_ROOM[groupId];if(!roomId)return;
  hueConfig=null;await fetchHueConfig();await fetchNowPlayingFeatures();
  try{const r=await fetch('/hue-get-state?room_id='+roomId);hueSnapshot[groupId]=await r.json();}catch(e){hueSnapshot[groupId]={};}
  hueActive[groupId]=true;hueLastTrack[groupId]='';hueLastStyle[groupId]='';
  saveHueState();renderPins();await triggerHueScene(groupId);
}
async function deactivateHue(groupId){
  hueActive[groupId]=false;
  delete hueSnapshot[groupId];delete hueLastTrack[groupId];delete hueCurrentScene[groupId];delete hueLastStyle[groupId];
  saveHueState();renderPins();
  const roomId=GROUP_HUE_ROOM[groupId];if(!roomId)return;
  fetch('/activate-hue-scene',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room_id:roomId,scene_name:'Lumineux'})}).catch(()=>{});
}
async function triggerHueScene(groupId){
  const roomId=GROUP_HUE_ROOM[groupId];if(!roomId||!hueActive[groupId])return;
  const s=state[groupId]||{};const streamId=s.stream||'';
  const styleId=getHueStyle(streamId);
  const roomName=getRoomNameForGroupPlan(groupId);
  if(!hueStreamScene[streamId]||hueStreamScene[streamId+'_style']!==styleId){
    hueStreamScene[streamId]=getHueSceneForStyle(roomName,styleId);
    hueStreamScene[streamId+'_style']=styleId;
  }
  const sceneName=hueStreamScene[streamId];
  try{
    const r=await fetch('/activate-hue-scene',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room_id:roomId,scene_name:sceneName})});
    const d=await r.json();
    if(d.status==='ok'){hueCurrentScene[groupId]=sceneName;saveHueState();renderPins();}
  }catch(e){}
}
async function hueAutoUpdate(){
  for(const groupId of Object.keys(hueActive)){
    if(!hueActive[groupId])continue;
    const s=state[groupId]||{};const streamId=s.stream||'';
    const streamPlaying=playingStreams.includes(streamId);
    const snapConnected=s.clients&&s.clients.some(c=>c.connected);
    const isActive=snapConnected&&streamPlaying&&!s.muted;
    if(!isActive){deactivateHue(groupId).catch(()=>{});continue;}
    const np=nowPlaying[streamId];
    const trackKey=np?(np.track+'|'+np.artist):'';
    if(trackKey&&trackKey!==hueLastTrack[groupId]){
      hueLastTrack[groupId]=trackKey;
      const newStyle=getHueStyle(streamId);
      if(newStyle&&newStyle!=='defaut'&&newStyle!==hueLastStyle[groupId]){
        hueLastStyle[groupId]=newStyle;await triggerHueScene(groupId);
      } else if(!hueLastStyle[groupId]&&newStyle){
        hueLastStyle[groupId]=newStyle;await triggerHueScene(groupId);
      }
    }
  }
}"""

content = content.replace(old, new)

# 2. Ajouter icône + vignette dans renderPins après les barres d'animation
old2 = "    if(isActive&&c) inner+='<div class=\"bars\" style=\"--c:'+c.main+'><span></span><span></span><span></span><span></span></div>';"
# Chercher la vraie ligne
import re
m = re.search(r"    if\(isActive&&c\) inner\+='<div class=\"bars\".*?</div>';", content)
if m:
    old2 = m.group(0)
    new2 = old2 + """
    // Bouton/vignette Hue
    if(GROUP_HUE_ROOM[pin.groupId]){
      const hOn=hueActive[pin.groupId];
      const canHue=isActive&&!s.muted;
      const curScene=hueCurrentScene[pin.groupId]||'';
      const imgFile=curScene&&SCENE_IMAGE_MAP[curScene]?SCENE_IMAGE_MAP[curScene]:'';
      if(hOn&&curScene){
        inner+='<div style="position:relative;width:70px;height:32px;border-radius:6px;overflow:hidden;border:1px solid '+(c?c.border:'#f5a623')+';flex-shrink:0;cursor:pointer;margin-left:2px" onclick="deactivateHue(\\''+pin.groupId+'\\')">'
          +(imgFile?'<img src="/hue-scenes/'+imgFile+'" style="width:100%;height:100%;object-fit:cover">':'<div style="width:100%;height:100%;background:#2a1a00"></div>')
          +'<div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.6),transparent)"></div>'
          +'<span style="position:absolute;bottom:1px;left:3px;font-size:8px;font-weight:600;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.8);white-space:nowrap;overflow:hidden;max-width:64px;text-overflow:ellipsis">'+curScene+'</span>'
          +'</div>';
      } else {
        inner+='<button onclick="'+(hOn?'deactivateHue':'activateHue')+'(\\''+pin.groupId+'\\')" style="-webkit-appearance:none;appearance:none;background:'+(hOn?'rgba(245,166,35,0.15)':'none')+';border:'+(hOn?'1px solid #f5a623':'none')+';border-radius:5px;cursor:'+(canHue?'pointer':'not-allowed')+';padding:2px 4px;color:'+(hOn?'#f5a623':(canHue?'#888':'#333'))+';display:flex;align-items:center;opacity:'+(canHue||hOn?1:0.4)+'"><svg width="14" height="14" viewBox="0 0 24 24" fill="none"><defs><linearGradient id="hg2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#ff0080"/><stop offset="50%" style="stop-color:#ffff00"/><stop offset="100%" style="stop-color:#0080ff"/></linearGradient></defs><path d="M9 21h6M12 3a6 6 0 0 1 6 6c0 2.22-1.21 4.16-3 5.2V17a1 1 0 0 1-1 1H10a1 1 0 0 1-1-1v-2.8C7.21 13.16 6 11.22 6 9a6 6 0 0 1 6-6z" stroke="url(#hg2)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>';
      }
    }"""
    content = content.replace(old2, new2)
    print("step2 OK")
else:
    print("step2 FAILED - bars line not found")

# 3. Ajouter hueAutoUpdate dans le setInterval
old3 = "fetchAll();\nsetInterval(fetchAll,10000);"
new3 = """fetchHueConfig();
fetchAll();
setInterval(()=>{fetchAll();if(Object.values(hueActive).some(v=>v))fetchNowPlayingFeatures().then(hueAutoUpdate);},10000);"""
content = content.replace(old3, new3)

open('/var/www/snapcast-ui/plan.html', 'w').write(content)
checks = ['GROUP_HUE_ROOM', 'activateHue', 'hueAutoUpdate', 'SCENE_IMAGE_MAP']
for c in checks:
    print(f"{'OK' if c in content else 'MISSING'}: {c}")
