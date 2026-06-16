import re, json, subprocess

content = open('/usr/local/bin/snapcast-api.py').read()

# Supprimer l'ancien do_POST
content = re.sub(r'\n    def do_POST\(self\):.*?(?=\n    def do_GET\(self\):)', '', content, flags=re.DOTALL)

new_post = '''
    def do_POST(self):
        from urllib.parse import urlparse
        import re as re2, os
        parsed = urlparse(self.path)
        if parsed.path == '/save-groups':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                VAR_MAP = {
                    'SDJ_GROUP':         '$SDJ_GROUP',
                    'CUISINE_GROUP':     '$CUISINE_GROUP',
                    'ATELIER_GROUP':     '$ATELIER_GROUP',
                    'FOURPAIN_GROUP':    '$FOURPAIN_GROUP',
                    'PARENTS_GROUP':     '$PARENTS_GROUP',
                    'LILIAN_GROUP':      '$LILIAN_GROUP',
                    'BIBLIO_GROUP':      '$BIBLIO_GROUP',
                    'THAIS_GROUP':       '$THAIS_GROUP',
                    'RPI_CUISINE_GROUP': '$RPI_CUISINE_GROUP',
                    'RPI_SALON_GROUP':   '$RPI_SALON_GROUP',
                    'RPI_BAIN_GROUP':    '$RPI_BAIN_GROUP',
                    'RPI_PARENTS_GROUP': '$RPI_PARENTS_GROUP',
                    'RPI_LILIAN_GROUP':  '$RPI_LILIAN_GROUP',
                    'RPI_THAIS_GROUP':   '$RPI_THAIS_GROUP',
                    'ECHOHUB_GROUP':     '$ECHOHUB_GROUP',
                }
                with open('/var/www/snapcast-ui/stream-groups.json', 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                with open('/usr/local/bin/snapcast-event.sh', 'r') as f:
                    script = f.read()
                new_cases = ''
                for g in data['groups']:
                    gid = g['id']
                    lines = ['  ' + gid + ')']
                    for var in g.get('force', []):
                        sh_var = VAR_MAP.get(var, '$' + var)
                        lines.append('    set_stream_force "' + sh_var + '" "' + gid + '"')
                    for var in g.get('if_idle', []):
                        sh_var = VAR_MAP.get(var, '$' + var)
                        lines.append('    set_stream_if_idle "' + sh_var + '" "' + gid + '"')
                    lines.append('    ;;')
                    new_cases += chr(10).join(lines) + chr(10)
                pattern = r'  maison\).*?esac'
                replacement = new_cases + 'esac'
                script = re2.sub(pattern, replacement, script, flags=re2.DOTALL)
                with open('/usr/local/bin/snapcast-event.sh', 'w') as f:
                    f.write(script)
                for g in data['groups']:
                    subprocess.Popen(['systemctl', 'restart', 'librespot-' + g['id']])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
'''

content = content.replace('    def do_GET(self):', new_post + '\n    def do_GET(self):')
open('/usr/local/bin/snapcast-api.py', 'w').write(content)
print('OK')
