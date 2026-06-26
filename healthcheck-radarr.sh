#!/bin/bash
COUNT=$(docker exec radarr ls /mnt/decypharr/__all__/ 2>&1 | wc -l)
if [ "$COUNT" -eq 0 ]; then
    echo "$(date) - FUSE mort dans Radarr, recreate..." >> /var/log/healthcheck-radarr.log
    cd /opt/mediastack && docker compose up -d --force-recreate radarr
    sleep 30
    curl -s -X POST "http://localhost:7878/api/v3/command" \
      -H "X-Api-Key: 18be05bc7daf481fa8000b28c6a46dd5" \
      -H "Content-Type: application/json" \
      -d '{"name":"MissingMoviesSearch"}' > /dev/null
    echo "$(date) - Radarr recreate + MissingMoviesSearch lancé" >> /var/log/healthcheck-radarr.log
else
    echo "$(date) - Radarr OK ($COUNT fichiers)" >> /var/log/healthcheck-radarr.log
fi
