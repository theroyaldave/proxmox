with open('/opt/mediastack/docker-compose.yml', 'r') as f:
    src = f.read()

readarr_service = """
  readarr:
    image: lscr.io/linuxserver/readarr:develop
    container_name: readarr
    restart: unless-stopped
    networks:
      - default_net
    volumes:
      - /opt/mediastack/config/readarr:/config
      - /mnt/mediastack/audiobooks:/audiobooks
      - /mnt/mediastack/ebooks:/ebooks
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
    ports:
      - 8787:8787

"""

# Insérer avant la section networks:
if 'readarr' in src:
    print('Readarr déjà présent, rien à faire')
else:
    src = src.replace('\nnetworks:', readarr_service + '\nnetworks:')
    with open('/opt/mediastack/docker-compose.yml', 'w') as f:
        f.write(src)
    print('OK - Readarr ajouté')

# Créer les dossiers sur le NAS
import os
os.makedirs('/mnt/mediastack/audiobooks', exist_ok=True)
os.makedirs('/mnt/mediastack/ebooks', exist_ok=True)
print('Dossiers créés')
