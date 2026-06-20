content = open('/usr/local/bin/../../../var/www/snapcast-ui/index.html').read()

# 1. Ajouter variable linkedStream après spotifyDevices
content = content.replace(
    'let state={},spotifyConnected=false,spotifyDevices=[],',
    'let state={},spotifyConnected=false,spotifyDevices=[],linkedStream=null,streamGroupsData=[],'
)

# 2. Stocker les données stream-groups dans fetchStreamGroups
content = content.replace(
    '    STREAM_GROUPS=data.groups.map(function(g){return g.id;});',
    '    STREAM_GROUPS=data.groups.map(function(g){return g.id;});\n    streamGroupsData=data.groups;'
)

# 3. Ajouter mapping VAR->groupId
VAR_MAP = """
const VAR_TO_GROUPID={
  "SDJ_GROUP":         "016e3537-578f-b2cd-5a37-48ebc1d5a8ea",
  "CUISINE_GROUP":     "3fa5da3f-8ba3-df55-feb8-c801659364f4",
  "ATELIER_GROUP":     "ca134b93-8951-9f02-b5fd-b5060d5458f0",
  "FOURPAIN_GROUP":    "19bea368-d8a7-51ef-bd12-4aec3f8f6ffa",
  "PARENTS_GROUP":     "4310351e-aa93-5793-7707-dd021425830b",
  "LILIAN_GROUP":      "6eb0e7b9-39fe-67ee-4707-2a121c6e111b",
  "BIBLIO_GROUP":      "49c944c2-e3da-c460-febb-203a0741e201",
  "THAIS_GROUP":       "f5a4a5bf-301d-aba2-dac6-3d7184937484",
  "RPI_CUISINE_GROUP": "1efe8146-e7b4-f934-ca31-a98a221f89d6",
  "RPI_SALON_GROUP":   "d5f5ba1d-27dc-4bb9-08dd-0f53ce33ce71",
  "RPI_BAIN_GROUP":    "a7ee841b-51eb-5b67-6de1-fba2104f0cdf",
  "RPI_PARENTS_GROUP": "4595c5db-7274-97ad-e8b6-bc997d6a2bd7",
  "RPI_LILIAN_GROUP":  "83ca2dc2-692c-0283-f5c3-4ebfe7768279",
  "RPI_THAIS_GROUP":   "fce87803-8613-471a-218e-a83250f02558",
  "ECHOHUB_GROUP":     "0cb6f6d4-de64-effa-d218-a2dbca2565bd",
};
function getStreamGroupMembers(streamId){
  const g=streamGroupsData.find(function(x){return x.id===streamId;});
  if(!g) return [];
  return (g.force||[]).concat(g.if_idle||[]).map(function(v){return VAR_TO_GROUPID[v];}).filter(Boolean);
}
function toggleLinked(streamId){
  linkedStream=linkedStream===streamId?null:streamId;
  renderGroups();
  renderStreams(Object.values(streamStatus).length?null:null);
  refresh();
}
async function adjustLinkedVolume(delta){
  if(!linkedStream) return;
  const members=getStreamGroupMembers(linkedStream);
  for(const gid of members){
    if(GROUP_OWNTONE[gid]){
      await setOwntoneVolume(gid,delta);
    } else if(GROUP_NS300[gid]){
      await setNs300Volume(gid,delta);
    }
  }
}
"""

content = content.replace(
    'const VAR_TO_GROUPID',
    '// VAR_TO_GROUPID already defined'
)
content = content.replace(
    'function renderStreams(streams){',
    VAR_MAP + 'function renderStreams(streams){'
)

# 4. Modifier renderStream pour les streams groupés — ajouter bouton lier + +/- globaux
old_render_groups = '''  document.getElementById("streams-bar-groups").innerHTML=streams.filter(s=>STREAM_GROUPS.includes(s.id)).map(renderStream).join("");'''

new_render_groups = '''  document.getElementById("streams-bar-groups").innerHTML=streams.filter(s=>STREAM_GROUPS.includes(s.id)).map(function(s){
    const base=renderStream(s);
    const playing=s.status==="playing";
    if(!playing) return base;
    const isLinked=linkedStream===s.id;
    const color=getStreamColor(s.id);
    const linkBtn='<button onclick="toggleLinked(\\\''+s.id+'\\\')" title="'+(isLinked?'Délier volumes':'Lier volumes')+'" style="-webkit-appearance:none;-moz-appearance:none;appearance:none;background:'+(isLinked?'rgba(255,160,0,0.15)':'none')+';border:'+(isLinked?'1px solid #c87000':'none')+';border-radius:5px;cursor:pointer;padding:2px 5px;color:'+(isLinked?'#ef9f27':'#555')+';display:flex;align-items:center"><i class="ti '+(isLinked?'ti-link':'ti-link-off')+'" style="font-size:12px"></i></button>';
    if(!isLinked) return base.replace('</div>',''+linkBtn+'</div>');
    const volCtrl='<div style="display:flex;align-items:center;gap:4px;margin-left:4px">'
      +'<button onclick="adjustLinkedVolume(-1)" style="-webkit-appearance:none;-moz-appearance:none;appearance:none;background:rgba(239,159,39,0.15);border:1px solid #c87000;border-radius:5px;color:#ef9f27;cursor:pointer;padding:1px 7px;font-size:14px;font-family:inherit">−</button>'
      +'<button onclick="adjustLinkedVolume(1)" style="-webkit-appearance:none;-moz-appearance:none;appearance:none;background:rgba(239,159,39,0.15);border:1px solid #c87000;border-radius:5px;color:#ef9f27;cursor:pointer;padding:1px 7px;font-size:14px;font-family:inherit">+</button>'
      +'</div>';
    return base.replace('</div>',''+linkBtn+volCtrl+'</div>');
  }).join("");'''

content = content.replace(old_render_groups, new_render_groups)

# 5. Modifier renderGroups pour colorer les boutons +/- des membres liés
# Trouver la ligne qui génère les boutons owntone volume et changer la couleur si lié
content = content.replace(
    "'background:#1e3a2f;border:1px solid #2d5a45;border-radius:8px;color:#5dcaa5;cursor:pointer;flex:1;height:42px;display:flex;align-items:center;justify-content:center;font-size:24px;font-family:inherit;font-weight:300'>−</button>'",
    "'background:'+(linkedStream&&getStreamGroupMembers(linkedStream).indexOf(id)>=0?'rgba(239,159,39,0.15)':'#1e3a2f')+';border:1px solid '+(linkedStream&&getStreamGroupMembers(linkedStream).indexOf(id)>=0?'#c87000':'#2d5a45')+';border-radius:8px;color:'+(linkedStream&&getStreamGroupMembers(linkedStream).indexOf(id)>=0?'#ef9f27':'#5dcaa5')+';cursor:pointer;flex:1;height:42px;display:flex;align-items:center;justify-content:center;font-size:24px;font-family:inherit;font-weight:300'>−</button>'"
)
content = content.replace(
    "'background:#1e3a2f;border:1px solid #2d5a45;border-radius:8px;color:#5dcaa5;cursor:pointer;flex:1;height:42px;display:flex;align-items:center;justify-content:center;font-size:24px;font-family:inherit;font-weight:300'>+</button>'",
    "'background:'+(linkedStream&&getStreamGroupMembers(linkedStream).indexOf(id)>=0?'rgba(239,159,39,0.15)':'#1e3a2f')+';border:1px solid '+(linkedStream&&getStreamGroupMembers(linkedStream).indexOf(id)>=0?'#c87000':'#2d5a45')+';border-radius:8px;color:'+(linkedStream&&getStreamGroupMembers(linkedStream).indexOf(id)>=0?'#ef9f27':'#5dcaa5')+';cursor:pointer;flex:1;height:42px;display:flex;align-items:center;justify-content:center;font-size:24px;font-family:inherit;font-weight:300'>+</button>'"
)

open('/var/www/snapcast-ui/index.html', 'w').write(content)
print('OK' if 'linkedStream' in content else 'FAILED')
