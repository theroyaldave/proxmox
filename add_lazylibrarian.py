with open('/opt/mediastack/docker-compose.yml', 'r') as f:
    src = f.read()

lazylibrarian_service = """
  lazylibrarian:
    image: lscr.io/linuxserver/lazylibrarian:latest
    container_name: lazylibrarian
    restart: unless-stopped
    networks:
      - default_net
    volumes:
      - /opt/mediastack/config/lazylibrarian:/config
      - /mnt/mediastack/downloads/books:/downloads
      - /mnt/mediastack/audiobooks:/audiobooks
      - /mnt/mediastack/ebooks:/ebooks
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
    ports:
      - 5299:5299

"""

if 'lazylibrarian' in src:
    print('LazyLibrarian déjà présent')
else:
    src = src.replace('\nnetworks:', lazylibrarian_service + '\nnetworks:')
    with open('/opt/mediastack/docker-compose.yml', 'w') as f:
        f.write(src)
    print('OK - LazyLibrarian ajouté')

import os
os.makedirs('/opt/mediastack/config/lazylibrarian', exist_ok=True)
os.makedirs('/mnt/mediastack/downloads/books', exist_ok=True)
print('Dossiers créés')
