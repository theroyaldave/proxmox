with open('/usr/local/bin/jeedom-notify.py', 'r') as f:
    src = f.read()

old = "HTTPServer(('127.0.0.1', 8090), Handler).serve_forever()"
new = "HTTPServer(('0.0.0.0', 8090), Handler).serve_forever()"

if old in src:
    src = src.replace(old, new)
    print('OK')
else:
    print('RATE')

with open('/usr/local/bin/jeedom-notify.py', 'w') as f:
    f.write(src)
