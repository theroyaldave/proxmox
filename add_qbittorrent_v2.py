with open('/opt/mediastack/docker-compose.yml', 'r') as f:
    src = f.read()

qbit_service = """
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    restart: unless-stopped
    networks:
      vpn_macvlan:
        ipv4_address: 192.168.4.59
      default_net: {}
    volumes:
      - /opt/mediastack/config/qbittorrent:/config
      - /opt/mediastack/config/qbittorrent/custom-cont-init.d:/custom-cont-init.d
      - /mnt/mediastack/downloads/books:/downloads
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - WEBUI_PORT=8080
    cap_add:
      - NET_ADMIN

"""

if 'qbittorrent' in src:
    print('qBittorrent déjà présent')
else:
    src = src.replace('\nnetworks:', qbit_service + '\nnetworks:')
    with open('/opt/mediastack/docker-compose.yml', 'w') as f:
        f.write(src)
    print('OK - qBittorrent ajouté')

import os
os.makedirs('/opt/mediastack/config/qbittorrent/custom-cont-init.d', exist_ok=True)

# Script de route VPN
vpn_script = """#!/bin/bash
sleep 5
while ! ip link show eth0 | grep -q "UP"; do sleep 1; done
ip route del default 2>/dev/null || true
ip route add default via 192.168.4.1 dev eth0 2>/dev/null || true
echo "VPN route set: $(ip route show default)"
"""

with open('/opt/mediastack/config/qbittorrent/custom-cont-init.d/01-vpn-route.sh', 'w') as f:
    f.write(vpn_script)

os.chmod('/opt/mediastack/config/qbittorrent/custom-cont-init.d/01-vpn-route.sh', 0o755)

# Config qBittorrent avec bypass auth pour 172.20.0.0/24
import os
os.makedirs('/opt/mediastack/config/qbittorrent/qBittorrent', exist_ok=True)

qbt_conf = """[BitTorrent]
Session\\DefaultSavePath=/downloads
Session\\TempPath=/downloads/temp

[Preferences]
WebUI\\AuthSubnetWhitelistEnabled=true
WebUI\\AuthSubnetWhitelist=172.20.0.0/24
WebUI\\LocalHostAuth=true
WebUI\\Port=8080
WebUI\\Username=admin
"""

conf_path = '/opt/mediastack/config/qbittorrent/qBittorrent/qBittorrent.conf'
if not os.path.exists(conf_path):
    with open(conf_path, 'w') as f:
        f.write(qbt_conf)
    print('Config qBittorrent créée avec bypass auth')
else:
    print('Config qBittorrent existante conservée')

print('Dossiers et scripts créés')
