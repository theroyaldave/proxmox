#!/bin/bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 --connect-timeout 2 http://127.0.0.1:8096/health 2>/dev/null)
if [ "$STATUS" != "200" ]; then
    echo "$(date) - Jellyfin KO (status=$STATUS), restart..." >> /var/log/healthcheck-jellyfin.log
    docker restart jellyfin
else
    echo "$(date) - Jellyfin OK" >> /var/log/healthcheck-jellyfin.log
fi
