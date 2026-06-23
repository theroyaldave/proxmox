import re

with open("/usr/local/bin/snapcast-api.py", "r") as f:
    c = f.read()

# Extraire le bloc hue-get-state de do_POST
m = re.search(
    r"\n        elif parsed\.path == '/hue-get-state':.*?(?=\n        elif |\n        else:)",
    c, re.DOTALL
)
if m:
    block = m.group()
    print(f"Found block: {len(block)} chars")
    c = c[:m.start()] + c[m.end():]
    print("Removed from do_POST")
else:
    print("NOT FOUND in do_POST")
    block = ""

# Insérer dans do_GET avant le else final
get_marker = "        else:\n            self.send_response(404)\n            self.end_headers()\n\nHTTPServer"
if block and get_marker in c:
    c = c.replace(get_marker, block + "\n        " + get_marker)
    print("Added to do_GET")
else:
    print("do_GET marker NOT FOUND")

with open("/usr/local/bin/snapcast-api.py", "w") as f:
    f.write(c)

# Vérifier position
post_pos = c.find("def do_POST")
get_pos = c.find("def do_GET(")
state_pos = c.find("'/hue-get-state'")
print(f"hue-get-state in do_GET: {state_pos > get_pos}")
print(f"count: {c.count('/hue-get-state')}")
