#!/bin/bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:8096/health)
if [ "$STATUS" != "200" ]; then
    echo "$(date) - Jellyfin KO (status=$STATUS), restart..." >> /var/log/healthcheck-jellyfin.log
    docker restart jellyfin
else
    echo "$(date) - Jellyfin OK" >> /var/log/healthcheck-jellyfin.log
fi
