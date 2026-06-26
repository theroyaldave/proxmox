#!/bin/bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:5055/api/v1/status)
if [ "$STATUS" != "200" ]; then
    echo "$(date) - Jellyseerr KO (status=$STATUS), restart..." >> /var/log/healthcheck-jellyseerr.log
    docker restart jellyseerr
else
    echo "$(date) - Jellyseerr OK" >> /var/log/healthcheck-jellyseerr.log
fi
