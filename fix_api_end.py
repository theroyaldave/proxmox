with open("/usr/local/bin/snapcast-api.py", "r") as f:
    content = f.read()

old_end = """            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
        else:
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            self.send_response(404)
            self.end_headers()

HTTPServer(('127.0.0.1', 8080), Handler).serve_forever()"""

new_end = """            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

HTTPServer(('127.0.0.1', 8080), Handler).serve_forever()"""

if old_end in content:
    content = content.replace(old_end, new_end)
    print("Fixed OK")
else:
    print("NOT FOUND")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(content)

import py_compile
try:
    py_compile.compile("/usr/local/bin/snapcast-api.py", doraise=True)
    print("SYNTAX OK")
except py_compile.PyCompileError as e:
    print(f"SYNTAX ERROR: {e}")
