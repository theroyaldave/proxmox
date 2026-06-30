#!/usr/bin/env python3
"""
Webhook receiver pour Radarr/Sonarr -> notification Jeedom
Ecoute sur le port 8090
Endpoints:
  POST /radarr-webhook
  POST /sonarr-webhook

Pour Sonarr: bufferise les episodes d'une meme serie pendant SONARR_BUFFER_SECONDS
avant d'envoyer une notification groupee, pour eviter une notif par episode
quand une saison complete est importee d'un coup.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, quote
import json
import urllib.request
import threading
import time

JEEDOM_BASE = "https://www.theroyaldave.fr/core/api/jeeApi.php"
JEEDOM_APIKEY = "3Mps4pnXGEkEHfF3yA3IZ5LcAMM02Nwh"
JEEDOM_ID = "17129"

RADARR_URL = "http://localhost:7878"
RADARR_APIKEY = "18be05bc7daf481fa8000b28c6a46dd5"

SONARR_URL = "http://localhost:8989"
SONARR_APIKEY = "0f1cbd43c8f24c22b8163e79ff43e6ce"

SONARR_BUFFER_SECONDS = 15


def sanitize_for_speech(text):
    """Nettoie le texte pour la synthese vocale (Alexa ne supporte pas certains caracteres)"""
    if not text:
        return text
    replacements = {
        '&': 'et',
        ':': ',',
        ';': ',',
        '"': '',
        "'": ' ',
        '/': ' ',
        '\\': ' ',
        '*': '',
        '#': '',
        '@': '',
        '%': ' pourcent',
        '+': ' plus ',
        '_': ' ',
        '~': '',
        '|': ' ',
        '<': '',
        '>': '',
        '[': '',
        ']': '',
        '{': '',
        '}': '',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Normaliser les espaces multiples
    text = ' '.join(text.split())
    return text

# Buffer pour grouper les episodes Sonarr par serie
_sonarr_buffer = {}  # series_id -> {"title": str, "episodes": [...], "timer": Timer}
_sonarr_lock = threading.Lock()


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


def flush_sonarr_buffer(series_id):
    """Appele apres le delai pour envoyer la notification groupee"""
    with _sonarr_lock:
        entry = _sonarr_buffer.pop(series_id, None)
    if not entry:
        return

    series_title = sanitize_for_speech(entry["title"])
    episodes = entry["episodes"]

    if len(episodes) > 1:
        by_season = {}
        for e in episodes:
            by_season.setdefault(e.get('seasonNumber', 0), []).append(e.get('episodeNumber', 0))

        parts = []
        for season, nums in sorted(by_season.items()):
            nums = sorted(nums)
            if nums[-1] - nums[0] + 1 == len(nums) and len(nums) > 1:
                parts.append(f"saison {season} épisodes {nums[0]} à {nums[-1]}")
            else:
                parts.append(f"saison {season} ({len(nums)} épisodes)")
        text = f"La série {series_title}, {', '.join(parts)}, est disponible"
    else:
        ep = episodes[0]
        season = ep.get('seasonNumber', '?')
        epnum = ep.get('episodeNumber', '?')
        text = f"La série {series_title} S{season:02d}E{epnum:02d} est disponible"

    notify_jeedom(text)


def add_to_sonarr_buffer(series_id, series_title, episode):
    with _sonarr_lock:
        if series_id not in _sonarr_buffer:
            _sonarr_buffer[series_id] = {"title": series_title, "episodes": [], "timer": None}
        entry = _sonarr_buffer[series_id]
        entry["episodes"].append(episode)

        # Annuler le timer precedent et en relancer un nouveau (debounce)
        if entry["timer"]:
            entry["timer"].cancel()
        timer = threading.Timer(SONARR_BUFFER_SECONDS, flush_sonarr_buffer, args=(series_id,))
        timer.daemon = True
        entry["timer"] = timer
        timer.start()


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
        buffered = False

        if parsed.path == '/radarr-webhook':
            if event_type in ('Download', 'Import'):
                movie = data.get('movie', {})
                movie_id = movie.get('id')
                year = movie.get('year', '')

                title = None
                if movie_id:
                    title = get_radarr_french_title(movie_id)
                if not title:
                    title = movie.get('title', 'Film inconnu')
                title = sanitize_for_speech(title)

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
                series_title = sanitize_for_speech(series_title)

                episodes = data.get('episodes', [])
                if episodes and series_id:
                    for ep in episodes:
                        add_to_sonarr_buffer(series_id, series_title, ep)
                    buffered = True
                elif episodes:
                    ep = episodes[0]
                    season = ep.get('seasonNumber', '?')
                    epnum = ep.get('episodeNumber', '?')
                    text = f"La série {series_title} S{season:02d}E{epnum:02d} est disponible"
                else:
                    text = f"La série {series_title} est disponible"

        notified = False
        if buffered:
            self.send_response(200)
        elif text:
            notified = notify_jeedom(text)
            self.send_response(200 if notified else 500)
        else:
            self.send_response(200)

        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'ok' if notified or buffered or not text else 'error',
            'notified': notified,
            'buffered': buffered,
            'text': text
        }).encode())


if __name__ == '__main__':
    print("Jeedom notify webhook listening on 0.0.0.0:8090")
    HTTPServer(('0.0.0.0', 8090), Handler).serve_forever()
