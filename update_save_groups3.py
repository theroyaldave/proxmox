import re

content = open('/usr/local/bin/snapcast-api.py').read()

old = """                # Detect new groups (not yet in snapserver.conf)
                import os"""

new = """                # Detect deleted groups and clean up
                import os
                try:
                    old_data = json.loads(open('/var/www/snapcast-ui/stream-groups.json').read())
                    old_ids = [g['id'] for g in old_data['groups']]
                    new_ids = [g['id'] for g in data['groups']]
                    for gid in old_ids:
                        if gid not in new_ids:
                            # Stop and disable service
                            subprocess.Popen(['systemctl', 'stop', 'librespot-' + gid])
                            subprocess.Popen(['systemctl', 'disable', 'librespot-' + gid])
                            svc_path = '/etc/systemd/system/librespot-' + gid + '.service'
                            if os.path.exists(svc_path):
                                os.remove(svc_path)
                            # Remove pipe from snapserver.conf
                            snap_conf = open('/etc/snapserver.conf').read()
                            snap_conf = re2.sub(r'source = pipe:///tmp/' + gid + r'[^\n]+\n', '', snap_conf)
                            open('/etc/snapserver.conf', 'w').write(snap_conf)
                            # Remove pipe
                            fifo = '/tmp/' + gid + '.fifo'
                            if os.path.exists(fifo):
                                os.remove(fifo)
                            # Remove from tmpfiles.d
                            tmpfiles = '/etc/tmpfiles.d/librespot-pipes.conf'
                            if os.path.exists(tmpfiles):
                                lines = open(tmpfiles).readlines()
                                lines = [l for l in lines if gid not in l]
                                open(tmpfiles, 'w').writelines(lines)
                            subprocess.Popen(['systemctl', 'daemon-reload'])
                            subprocess.Popen(['systemctl', 'restart', 'snapserver'])
                except Exception:
                    pass

                # Detect new groups (not yet in snapserver.conf)"""

content = content.replace(old, new)
open('/usr/local/bin/snapcast-api.py', 'w').write(content)
print('OK' if 'Detect deleted groups' in content else 'FAILED')
