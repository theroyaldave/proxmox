with open('/opt/mediastack/docker-compose.yml', 'r') as f:
    content = f.read()

old = "      - /opt/mediastack/scripts:/scripts\n    environment:\n      - PUID=1000\n      - PGID=1000\n      - TZ=Europe/Paris\n    ports:\n      - 7878:7878"
new = "      - /opt/mediastack/scripts:/scripts\n    volumes_from:\n      - decypharr:ro\n    environment:\n      - PUID=1000\n      - PGID=1000\n      - TZ=Europe/Paris\n    ports:\n      - 7878:7878"

if old in content:
    content = content.replace(old, new)
    with open('/opt/mediastack/docker-compose.yml', 'w') as f:
        f.write(content)
    print("OK - volumes_from ajouté à Radarr")
else:
    print("ERREUR - pattern non trouvé, vérifier le fichier")
