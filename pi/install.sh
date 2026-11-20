#!/bin/sh
# Run from a checkout with: sudo sh pi/install.sh
set -eu
if [ "$(id -u)" -ne 0 ]; then echo 'Run: sudo sh pi/install.sh' >&2; exit 1; fi
src=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
pin=ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975
for name in pi/pi_bridge.py pi/pairing_agent.py pi/patch_nxbt.py pi/bluez_compat.py pi/seedsow-input.service pc/controller_protocol.py; do
    test -f "$src/$name" || { echo "Missing installer file: $name" >&2; exit 1; }
done
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git python3 python3-dbus python3-gi bluez rfkill
if ! command -v hciconfig >/dev/null 2>&1; then
    echo 'This NXBT build needs hciconfig. Install the BlueZ package containing that tool for your Pi OS, then rerun.' >&2
    exit 1
fi
stage=$(mktemp -d /tmp/seedsow-install.XXXXXXXX)
trap 'rm -rf -- "$stage"' EXIT HUP INT TERM
git init -q "$stage/nxbt"
git -C "$stage/nxbt" remote add origin https://github.com/Brikwerk/nxbt.git
git -C "$stage/nxbt" fetch -q --depth 1 origin "$pin"
git -C "$stage/nxbt" checkout -q --detach FETCH_HEAD
test "$(git -C "$stage/nxbt" rev-parse HEAD)" = "$pin"
python3 "$src/pi/patch_nxbt.py" "$stage/nxbt/nxbt"
if systemctl cat seedsow-input.service >/dev/null 2>&1; then
    systemctl stop seedsow-input.service
fi
install -d -m 755 /opt/seedsow-input/pi /opt/seedsow-input/pc /opt/seedsow-input/vendor
for name in pi_bridge.py pairing_agent.py; do
    install -m 644 "$src/pi/$name" "/opt/seedsow-input/pi/$name"
done
install -m 644 "$src/pc/controller_protocol.py" /opt/seedsow-input/pc/controller_protocol.py
cp -a "$stage/nxbt/nxbt" /opt/seedsow-input/vendor/
install -m 644 "$stage/nxbt/LICENSE" /opt/seedsow-input/vendor/NXBT-LICENSE.txt
python3 - <<'PY'
import json, os, secrets, tempfile
from pathlib import Path
path = Path('/etc/seedsow-input.json')
config = json.loads(path.read_text()) if path.exists() else {}
config.setdefault('token', secrets.token_hex(32))
config.setdefault('port', 39391)
config.setdefault('bind', '0.0.0.0')
config['nxbt_path'] = '/opt/seedsow-input/vendor'
config['bridge_version'] = 'pi-compat-1'
if not isinstance(config['token'], str) or len(config['token']) < 32:
    raise ValueError('Existing bridge token is invalid. Inspect /etc/seedsow-input.json before continuing.')
if type(config['port']) is not int or not 1 <= config['port'] <= 65535:
    raise ValueError('Existing bridge port is invalid. Inspect /etc/seedsow-input.json before continuing.')
with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, prefix='.seedsow-input-', delete=False) as output:
    temporary = Path(output.name)
    try:
        os.chmod(temporary, 0o600)
        output.write(json.dumps(config, indent=2)+'\n')
        output.flush()
        os.fsync(output.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
try:
    temporary.replace(path)
finally:
    temporary.unlink(missing_ok=True)
PY
install -m 644 "$src/pi/seedsow-input.service" /etc/systemd/system/seedsow-input.service
systemctl daemon-reload
systemctl enable --now seedsow-input.service
systemctl --no-pager --full status seedsow-input.service
echo 'Next: python3 pi/export_connection.py --output ~/seedsow-connection.json'
