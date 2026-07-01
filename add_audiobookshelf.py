with open('/opt/mediastack/docker-compose.yml', 'r') as f:
    src = f.read()

audiobookshelf_service = """
  audiobookshelf:
    image: ghcr.io/advplyr/audiobookshelf:latest
    container_name: audiobookshelf
    restart: unless-stopped
    networks:
      - default_net
    volumes:
      - /mnt/mediastack/audiobooks:/audiobooks
      - /mnt/mediastack/ebooks:/ebooks
      - /opt/mediastack/config/audiobookshelf:/config
      - /opt/mediastack/config/audiobookshelf/metadata:/metadata
    environment:
      - AUDIOBOOKSHELF_UID=1000
      - AUDIOBOOKSHELF_GID=1000
      - TZ=Europe/Paris
    ports:
      - 13378:80

"""

if 'audiobookshelf' in src:
    print('Audiobookshelf déjà présent')
else:
    src = src.replace('\nnetworks:', audiobookshelf_service + '\nnetworks:')
    with open('/opt/mediastack/docker-compose.yml', 'w') as f:
        f.write(src)
    print('OK - Audiobookshelf ajouté')
