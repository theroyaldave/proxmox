#!/usr/bin/env python3
"""
Webhook receiver pour Radarr/Sonarr -> notification Jeedom
Ecoute sur le port 8090
Endpoints:
  POST /radarr-webhook
  POST /sonarr-webhook
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, quote
import json
import urllib.request

JEEDOM_BASE = "https://www.theroyaldave.fr/core/api/jeeApi.php"
JEEDOM_APIKEY = "3Mps4pnXGEkEHfF3yA3IZ5LcAMM02Nwh"
JEEDOM_ID = "17129"

def notify_jeedom(text):
    url = f"{JEEDOM_BASE}?plugin=virtual&type=event&apikey={JEEDOM_APIKEY}&id={JEEDOM_ID}&value={quote(text)}"
    try:
        req = urllib.request.Request(url, method="GET")
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"Erreur notification Jeedom: {e}")
        return False

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}

        event_type = data.get('eventType', '')
        text = None

        if parsed.path == '/radarr-webhook':
            # On ne notifie que sur Download/Import (film disponible)
            if event_type in ('Download', 'Import'):
                movie = data.get('movie', {})
                title = movie.get('title', 'Film inconnu')
                year = movie.get('year', '')
                text = f"Le film {title} ({year}) est disponible" if year else f"Le film {title} est disponible"

        elif parsed.path == '/sonarr-webhook':
            if event_type in ('Download', 'Import'):
                series = data.get('series', {})
                series_title = series.get('title', 'Série inconnue')
                episodes = data.get('episodes', [])
                if episodes:
                    ep = episodes[0]
                    season = ep.get('seasonNumber', '?')
                    epnum = ep.get('episodeNumber', '?')
                    text = f"Le film {series_title} S{season:02d}E{epnum:02d} est disponible"
                else:
                    text = f"Le film {series_title} est disponible"

        if text:
            success = notify_jeedom(text)
            self.send_response(200 if success else 500)
        else:
            # Event ignoré (pas Download/Import) - on répond 200 quand même
            self.send_response(200)

        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'notified': text is not None}).encode())

if __name__ == '__main__':
    print("Jeedom notify webhook listening on 127.0.0.1:8090")
    HTTPServer(('127.0.0.1', 8090), Handler).serve_forever()
