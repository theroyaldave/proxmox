import re

content = open('/usr/local/bin/snapcast-api.py').read()

# Find the save-groups handler and add auto-creation of new groups
old = """                for g in data['groups']:
                    subprocess.Popen(['systemctl', 'restart', 'librespot-' + g['id']])"""

new = """                # Detect new groups (not yet in snapserver.conf)
                import os
                snapserver_conf = open('/etc/snapserver.conf').read()
                for g in data['groups']:
                    gid = g['id']
                    if 'name=' + gid not in snapserver_conf:
                        # New group - create pipe, librespot service, snapserver entry
                        fifo_path = '/tmp/' + gid + '.fifo'
                        if not os.path.exists(fifo_path):
                            os.mkfifo(fifo_path)
                            os.chmod(fifo_path, 0o666)
                        # Add to tmpfiles.d
                        tmpfiles = '/etc/tmpfiles.d/librespot-pipes.conf'
                        tmpfiles_content = open(tmpfiles).read() if os.path.exists(tmpfiles) else ''
                        if fifo_path not in tmpfiles_content:
                            with open(tmpfiles, 'a') as f:
                                f.write('p ' + fifo_path + ' 0666 root root -' + chr(10))
                        # Create cache dir
                        os.makedirs('/var/cache/librespot/' + gid, exist_ok=True)
                        # Create librespot service
                        label = g.get('label', gid)
                        service = chr(10).join([
                            '[Unit]',
                            'Description=Librespot ' + label,
                            'After=network.target',
                            '[Service]',
                            'ExecStart=/root/.cargo/bin/librespot --name "' + label + '" --backend pipe --device ' + fifo_path + ' --bitrate 320 --device-type speaker --cache /var/cache/librespot/' + gid + ' --cache-size-limit 314572800 --onevent /usr/local/bin/snapcast-event.sh',
                            'Environment=DEVICE_NAME=' + gid,
                            'Restart=always',
                            'RestartSec=5',
                            '[Install]',
                            'WantedBy=multi-user.target',
                        ])
                        with open('/etc/systemd/system/librespot-' + gid + '.service', 'w') as f:
                            f.write(service)
                        # Add stream to snapserver.conf
                        with open('/etc/snapserver.conf', 'a') as f:
                            f.write('source = pipe://' + fifo_path + '?name=' + gid + '&sampleformat=44100:16:2&codec=flac' + chr(10))
                        subprocess.Popen(['systemctl', 'daemon-reload'])
                        subprocess.Popen(['systemctl', 'enable', '--now', 'librespot-' + gid])
                        subprocess.Popen(['systemctl', 'restart', 'snapserver'])
                    else:
                        subprocess.Popen(['systemctl', 'restart', 'librespot-' + gid])"""

content = content.replace(old, new)
open('/usr/local/bin/snapcast-api.py', 'w').write(content)
print('OK' if 'Detect new groups' in content else 'FAILED')
