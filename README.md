# arine-tools-greenhouse-python

Arine: Tools: Greenhouse (Python)

Setup:

```shell
scripts/sync-development-requirements.sh
```

Run (Example): Downloads all resumes.. make sure you remove `.cache` before hand if a full rescan is needed vs resuming
a pull.

```shell
arine-tools-greenhouse recruiting \
    --firefox-profile-path="/Users/sspencer/Library/Application Support/Firefox/Profiles/10ox28ao.default-release" \
    applications \
    --job-title="Senior Full Stack Software Engineer (140)" \
    offline \
    ~/resumes-offline/
```
