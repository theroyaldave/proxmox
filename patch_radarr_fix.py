with open('/opt/mediastack/docker-compose.yml', 'r') as f:
    content = f.read()

old_radarr = ("      - /opt/mediastack/scripts:/scripts\n"
              "    depends_on:\n"
              "      decypharr:\n"
              "        condition: service_healthy\n"
              "    volumes_from:\n"
              "      - decypharr:ro\n"
              "    environment:\n"
              "      - PUID=1000\n"
              "      - PGID=1000\n"
              "      - TZ=Europe/Paris\n"
              "    ports:\n"
              "      - 7878:7878")

new_radarr = ("      - /opt/mediastack/scripts:/scripts\n"
              "      - type: bind\n"
              "        source: /opt/mediastack/decypharr-mount/decypharr\n"
              "        target: /mnt/decypharr\n"
              "        bind:\n"
              "          propagation: rshared\n"
              "    depends_on:\n"
              "      decypharr:\n"
              "        condition: service_healthy\n"
              "    environment:\n"
              "      - PUID=1000\n"
              "      - PGID=1000\n"
              "      - TZ=Europe/Paris\n"
              "    ports:\n"
              "      - 7878:7878")

if old_radarr in content:
    content = content.replace(old_radarr, new_radarr)
    print("OK - Radarr restauré avec bind mount rshared")
else:
    print("ERREUR - pattern non trouvé")

with open('/opt/mediastack/docker-compose.yml', 'w') as f:
    f.write(content)
