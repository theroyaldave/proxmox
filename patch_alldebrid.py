import json

with open('/app/config.json', 'r') as f:
    config = json.load(f)

alldebrid = {
    "provider": "alldebrid",
    "name": "AllDebrid Primary",
    "api_key": "WtiLGYvzdm7FPVa5DzIe",
    "download_api_keys": [
        "WtiLGYvzdm7FPVa5DzIe"
    ],
    "download_uncached": False,
    "rate_limit": "250/minute",
    "minimum_free_slot": 1,
    "torrents_refresh_interval": "10m",
    "download_links_refresh_interval": "5m",
    "workers": 200,
    "auto_expire_links_after": "3d"
}

config['debrids'].insert(0, alldebrid)

with open('/app/config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("OK - AllDebrid ajouté en premier provider")
print(f"Providers: {[d['name'] for d in config['debrids']]}")
