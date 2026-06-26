#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

RADARR_URL = "http://localhost:7878"
RADARR_KEY = "18be05bc7daf481fa8000b28c6a46dd5"
RD_KEY = "AGWMLUEMYM7NPZ5PKNL7IO3KVRHWK65GIZ5U5FOJQIPAQJWFN5FA"
PORT = 7879
HTML_FILE = "/opt/mediastack/rd-cache-checker.html"

HTML = open(HTML_FILE).read() if os.path.exists(HTML_FILE) else "<h1>rd-cache-checker.html manquant</h1>"

class ProxyHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[rd-proxy] {self.path} {args[1] if len(args)>1 else ''}")

    def send_cors(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_cors()

    def fetch(self, url, headers=None, data=None):
        req = urllib.request.Request(url, headers=headers or {}, data=data)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def do_GET(self):
        path = self.path.split("?")[0]
        params = {}
        if "?" in self.path:
            for p in self.path.split("?")[1].split("&"):
                if "=" in p:
                    k, v = p.split("=", 1)
                    params[k] = v

        if path == "/rdchecker":
            self.send_cors(200, "text/html; charset=utf-8")
            self.wfile.write(HTML.encode())

        elif path == "/movies":
            data = self.fetch(f"{RADARR_URL}/api/v3/movie",
                              headers={"X-Api-Key": RADARR_KEY})
            if isinstance(data, list):
                missing = [
                    {"id": m["id"], "title": m["title"], "year": m.get("year", "")}
                    for m in data
                    if m.get("monitored") and not m.get("hasFile") and m.get("status") == "released"
                ]
                self.send_cors()
                self.wfile.write(json.dumps(missing).encode())
            else:
                self.send_cors(500)
                self.wfile.write(json.dumps(data).encode())

        elif path == "/releases":
            movie_id = params.get("movieId", "")
            releases = self.fetch(f"{RADARR_URL}/api/v3/release?movieId={movie_id}",
                                  headers={"X-Api-Key": RADARR_KEY})
            if not isinstance(releases, list):
                self.send_cors(500)
                self.wfile.write(json.dumps(releases).encode())
                return

            with_hash = [r for r in releases if r.get("infoHash")]
            if not with_hash:
                self.send_cors()
                self.wfile.write(json.dumps([]).encode())
                return

            hashes = list(set(r["infoHash"].lower() for r in with_hash))
            rd_data = self.fetch(
                f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{'/'.join(hashes)}",
                headers={"Authorization": f"Bearer {RD_KEY}"}
            )

            result = []
            for r in with_hash:
                h = r["infoHash"].lower()
                cached = isinstance(rd_data, dict) and h in rd_data and bool(rd_data[h])
                result.append({
                    "guid": r.get("guid"),
                    "title": r.get("title"),
                    "quality": r.get("quality", {}).get("quality", {}).get("name", ""),
                    "size": r.get("size", 0),
                    "seeders": r.get("seeders", 0),
                    "indexer": r.get("indexer", ""),
                    "infoHash": h,
                    "cached": cached
                })

            result.sort(key=lambda x: (not x["cached"], -x["seeders"]))
            self.send_cors()
            self.wfile.write(json.dumps(result).encode())

        else:
            self.send_cors(404)
            self.wfile.write(json.dumps({"error": "not found"}).encode())

    def do_POST(self):
        if self.path == "/grab":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            guid = body.get("guid")
            result = self.fetch(
                f"{RADARR_URL}/api/v3/release",
                headers={"X-Api-Key": RADARR_KEY, "Content-Type": "application/json"},
                data=json.dumps({"guid": guid, "indexerId": 0}).encode()
            )
            self.send_cors()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_cors(404)
            self.wfile.write(json.dumps({"error": "not found"}).encode())

if __name__ == "__main__":
    print(f"[rd-proxy] Démarrage sur port {PORT}")
    HTTPServer(("0.0.0.0", PORT), ProxyHandler).serve_forever()
