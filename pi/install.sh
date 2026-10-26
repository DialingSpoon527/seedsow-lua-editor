#!/bin/sh
# Run from a checkout with: sudo sh pi/install.sh
set -eu
if [ "$(id -u)" -ne 0 ]; then echo 'Run: sudo sh pi/install.sh' >&2; exit 1; fi
src=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
pin=ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git python3 python3-dbus python3-gi bluez rfkill
stage=$(mktemp -d /tmp/seedsow-install.XXXXXXXX)
trap 'rm -rf -- "$stage"' EXIT HUP INT TERM
git init -q "$stage/nxbt"
git -C "$stage/nxbt" remote add origin https://github.com/Brikwerk/nxbt.git
git -C "$stage/nxbt" fetch -q --depth 1 origin "$pin"
git -C "$stage/nxbt" checkout -q --detach FETCH_HEAD
test "$(git -C "$stage/nxbt" rev-parse HEAD)" = "$pin"
python3 "$src/pi/patch_nxbt.py" "$stage/nxbt/nxbt"
systemctl stop seedsow-input.service 2>/dev/null || true
install -d -m 755 /opt/seedsow-input/pi /opt/seedsow-input/pc /opt/seedsow-input/vendor
for name in pi_bridge.py pairing_agent.py; do
    install -m 644 "$src/pi/$name" "/opt/seedsow-input/pi/$name"
done
install -m 644 "$src/pc/protocol.py" /opt/seedsow-input/pc/protocol.py
cp -a "$stage/nxbt/nxbt" /opt/seedsow-input/vendor/
install -m 644 "$stage/nxbt/LICENSE" /opt/seedsow-input/vendor/NXBT-LICENSE.txt
python3 - <<'PY'
import json, os, secrets
from pathlib import Path
path = Path('/etc/seedsow-input.json')
config = json.loads(path.read_text()) if path.exists() else {}
config.setdefault('token', secrets.token_hex(32))
config.setdefault('port', 39391)
config['bind'] = '0.0.0.0'
config['nxbt_path'] = '/opt/seedsow-input/vendor'
path.touch(mode=0o600, exist_ok=True)
os.chmod(path, 0o600)
path.write_text(json.dumps(config, indent=2)+'\n')
PY
install -m 644 "$src/pi/seedsow-input.service" /etc/systemd/system/seedsow-input.service
systemctl daemon-reload
systemctl enable --now seedsow-input.service
systemctl --no-pager --full status seedsow-input.service
echo 'Next: python3 pi/export_connection.py --output ~/seedsow-connection.json'
