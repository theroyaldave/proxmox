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

RADARR_URL = "http://localhost:7878"
RADARR_APIKEY = "18be05bc7daf481fa8000b28c6a46dd5"

SONARR_URL = "http://localhost:8989"
SONARR_APIKEY = "0f1cbd43c8f24c22b8163e79ff43e6ce"

def notify_jeedom(text):
    url = f"{JEEDOM_BASE}?plugin=virtual&type=event&apikey={JEEDOM_APIKEY}&id={JEEDOM_ID}&value={quote(text)}"
    try:
        req = urllib.request.Request(url, method="GET", headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) jeedom-notify/1.0"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read()
        print(f"Jeedom OK: status={resp.status} body={body[:200]}")
        return True
    except Exception as e:
        print(f"Erreur notification Jeedom: {e}")
        return False

def get_radarr_french_title(movie_id):
    """Recupere le titre francais reel depuis l'API Radarr (le webhook envoie parfois le titre VO)"""
    try:
        url = f"{RADARR_URL}/api/v3/movie/{movie_id}?apikey={RADARR_APIKEY}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        return data.get('title')
    except Exception as e:
        print(f"Erreur recuperation titre Radarr: {e}")
        return None

def get_sonarr_french_title(series_id):
    """Recupere le titre francais reel depuis l'API Sonarr"""
    if not SONARR_APIKEY:
        return None
    try:
        url = f"{SONARR_URL}/api/v3/series/{series_id}?apikey={SONARR_APIKEY}"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        return data.get('title')
    except Exception as e:
        print(f"Erreur recuperation titre Sonarr: {e}")
        return None

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
            if event_type in ('Download', 'Import'):
                movie = data.get('movie', {})
                movie_id = movie.get('id')
                year = movie.get('year', '')

                # Tenter de recuperer le titre francais via l'API (plus fiable que le webhook)
                title = None
                if movie_id:
                    title = get_radarr_french_title(movie_id)
                if not title:
                    title = movie.get('title', 'Film inconnu')

                text = f"Le film {title} ({year}) est disponible" if year else f"Le film {title} est disponible"

        elif parsed.path == '/sonarr-webhook':
            if event_type in ('Download', 'Import'):
                series = data.get('series', {})
                series_id = series.get('id')

                series_title = None
                if series_id:
                    series_title = get_sonarr_french_title(series_id)
                if not series_title:
                    series_title = series.get('title', 'Série inconnue')

                episodes = data.get('episodes', [])
                if episodes:
                    ep = episodes[0]
                    season = ep.get('seasonNumber', '?')
                    epnum = ep.get('episodeNumber', '?')
                    text = f"Le film {series_title} S{season:02d}E{epnum:02d} est disponible"
                else:
                    text = f"Le film {series_title} est disponible"

        notified = False
        if text:
            notified = notify_jeedom(text)
            self.send_response(200 if notified else 500)
        else:
            self.send_response(200)

        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok' if notified or not text else 'error', 'notified': notified, 'text': text}).encode())

if __name__ == '__main__':
    print("Jeedom notify webhook listening on 0.0.0.0:8090")
    HTTPServer(('0.0.0.0', 8090), Handler).serve_forever()
