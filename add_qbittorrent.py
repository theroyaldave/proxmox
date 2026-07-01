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
      - /mnt/mediastack/downloads/books:/downloads
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - WEBUI_PORT=8080

"""

if 'qbittorrent' in src:
    print('qBittorrent déjà présent')
else:
    src = src.replace('\nnetworks:', qbit_service + '\nnetworks:')
    with open('/opt/mediastack/docker-compose.yml', 'w') as f:
        f.write(src)
    print('OK - qBittorrent ajouté')

import os
os.makedirs('/mnt/mediastack/downloads/books', exist_ok=True)
print('Dossier downloads/books créé')
