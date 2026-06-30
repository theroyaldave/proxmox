import re

with open('/usr/local/bin/jeedom-notify.py', 'r') as f:
    src = f.read()

old = '''def notify_jeedom(text):
    url = f"{JEEDOM_BASE}?plugin=virtual&type=event&apikey={JEEDOM_APIKEY}&id={JEEDOM_ID}&value={quote(text)}"
    try:
        req = urllib.request.Request(url, method="GET")
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"Erreur notification Jeedom: {e}")
        return False'''

new = '''def notify_jeedom(text):
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
        return False'''

if old in src:
    src = src.replace(old, new)
    print('notify_jeedom OK')
else:
    print('notify_jeedom RATE')

old2 = '''        if text:
            success = notify_jeedom(text)
            self.send_response(200 if success else 500)
        else:
            # Event ignoré (pas Download/Import) - on répond 200 quand même
            self.send_response(200)

        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'notified': text is not None}).encode())'''

new2 = '''        notified = False
        if text:
            notified = notify_jeedom(text)
            self.send_response(200 if notified else 500)
        else:
            self.send_response(200)

        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok' if notified or not text else 'error', 'notified': notified, 'text': text}).encode())'''

if old2 in src:
    src = src.replace(old2, new2)
    print('do_POST OK')
else:
    print('do_POST RATE')

with open('/usr/local/bin/jeedom-notify.py', 'w') as f:
    f.write(src)
print('done')
