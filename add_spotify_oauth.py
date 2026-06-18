import re

content = open('/usr/local/bin/snapcast-api.py').read()

spotify_code = '''
    def do_GET_spotify(self, parsed):
        import urllib.parse, urllib.request, base64, time
        config = json.loads(open('/var/lib/snapcast-spotify/config.json').read())
        tokens_file = '/var/lib/snapcast-spotify/tokens.json'

        if parsed.path == '/spotify-auth':
            # Redirect to Spotify OAuth
            params = urllib.parse.urlencode({
                'client_id': config['client_id'],
                'response_type': 'code',
                'redirect_uri': config['redirect_uri'],
                'scope': config['scopes'],
            })
            self.send_response(302)
            self.send_header('Location', 'https://accounts.spotify.com/authorize?' + params)
            self.end_headers()

        elif parsed.path == '/spotify-callback':
            # Exchange code for tokens
            params = urllib.parse.parse_qs(parsed.query)
            code = params.get('code', [''])[0]
            if not code:
                self.send_response(400)
                self.end_headers()
                return
            auth = base64.b64encode((config['client_id'] + ':' + config['client_secret']).encode()).decode()
            req = urllib.request.Request(
                'https://accounts.spotify.com/api/token',
                data=urllib.parse.urlencode({
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': config['redirect_uri'],
                }).encode(),
                headers={'Authorization': 'Basic ' + auth, 'Content-Type': 'application/x-www-form-urlencoded'}
            )
            try:
                resp = urllib.request.urlopen(req)
                tokens = json.loads(resp.read())
                tokens['expires_at'] = time.time() + tokens.get('expires_in', 3600)
                with open(tokens_file, 'w') as f:
                    json.dump(tokens, f)
                # Redirect back to UI with success
                self.send_response(302)
                self.send_header('Location', '/?spotify=connected')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif parsed.path == '/spotify-status':
            # Check if token is valid
            try:
                tokens = json.loads(open(tokens_file).read())
                connected = time.time() < tokens.get('expires_at', 0)
                # Try to refresh if expired
                if not connected and 'refresh_token' in tokens:
                    auth = base64.b64encode((config['client_id'] + ':' + config['client_secret']).encode()).decode()
                    req = urllib.request.Request(
                        'https://accounts.spotify.com/api/token',
                        data=urllib.parse.urlencode({
                            'grant_type': 'refresh_token',
                            'refresh_token': tokens['refresh_token'],
                        }).encode(),
                        headers={'Authorization': 'Basic ' + auth, 'Content-Type': 'application/x-www-form-urlencoded'}
                    )
                    resp = urllib.request.urlopen(req, timeout=5)
                    new_tokens = json.loads(resp.read())
                    tokens['access_token'] = new_tokens['access_token']
                    tokens['expires_at'] = time.time() + new_tokens.get('expires_in', 3600)
                    with open(tokens_file, 'w') as f:
                        json.dump(tokens, f)
                    connected = True
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'connected': connected}).encode())
            except:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'connected': False}).encode())

        elif parsed.path == '/spotify-devices':
            # Get available Spotify devices
            try:
                tokens = json.loads(open(tokens_file).read())
                req = urllib.request.Request(
                    'https://api.spotify.com/v1/me/player/devices',
                    headers={'Authorization': 'Bearer ' + tokens['access_token']}
                )
                resp = urllib.request.urlopen(req, timeout=5)
                data = json.loads(resp.read())
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'devices': [], 'error': str(e)}).encode())

        elif parsed.path == '/spotify-transfer':
            # Transfer playback to device
            params = urllib.parse.parse_qs(parsed.query)
            device_name = params.get('name', [''])[0]
            try:
                tokens = json.loads(open(tokens_file).read())
                # Get devices to find device_id by name
                req = urllib.request.Request(
                    'https://api.spotify.com/v1/me/player/devices',
                    headers={'Authorization': 'Bearer ' + tokens['access_token']}
                )
                resp = urllib.request.urlopen(req, timeout=5)
                devices = json.loads(resp.read()).get('devices', [])
                device_id = None
                for d in devices:
                    if d['name'] == device_name:
                        device_id = d['id']
                        break
                if device_id:
                    req2 = urllib.request.Request(
                        'https://api.spotify.com/v1/me/player',
                        data=json.dumps({'device_ids': [device_id], 'play': True}).encode(),
                        headers={'Authorization': 'Bearer ' + tokens['access_token'], 'Content-Type': 'application/json'},
                        method='PUT'
                    )
                    urllib.request.urlopen(req2, timeout=5)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'ok', 'device_id': device_id}).encode())
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'not_found', 'available': [d['name'] for d in devices]}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
        else:
            return False
        return True
'''

# Add do_GET_spotify call in do_GET
old = "    def do_GET(self):\n        parsed = urlparse(self.path)"
new = "    def do_GET(self):\n        parsed = urlparse(self.path)\n        if parsed.path in ['/spotify-auth','/spotify-callback','/spotify-status','/spotify-devices','/spotify-transfer']:\n            self.do_GET_spotify(parsed)\n            return"

content = content.replace(old, new)

# Insert do_GET_spotify before do_GET
content = content.replace("    def do_GET(self):", spotify_code + "\n    def do_GET(self):")

open('/usr/local/bin/snapcast-api.py', 'w').write(content)
print('OK' if 'spotify-auth' in content else 'FAILED')
