with open('/opt/mediastack/docker-compose.yml', 'r') as f:
    content = f.read()

# Radarr - ajouter depends_on avant volumes_from
old_radarr = "    volumes_from:\n      - decypharr:ro\n    environment:\n      - PUID=1000\n      - PGID=1000\n      - TZ=Europe/Paris\n    ports:\n      - 7878:7878"
new_radarr = "    depends_on:\n      decypharr:\n        condition: service_healthy\n    volumes_from:\n      - decypharr:ro\n    environment:\n      - PUID=1000\n      - PGID=1000\n      - TZ=Europe/Paris\n    ports:\n      - 7878:7878"

if old_radarr in content:
    content = content.replace(old_radarr, new_radarr)
    print("OK - depends_on ajouté à Radarr")
else:
    print("ERREUR - pattern Radarr non trouvé")

with open('/opt/mediastack/docker-compose.yml', 'w') as f:
    f.write(content)
