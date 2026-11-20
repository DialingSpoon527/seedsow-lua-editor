"""Export only PC connection settings; keep the resulting file private."""
import argparse
import json
import os
import socket
import subprocess
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=Path.home()/'seedsow-connection.json')
    p.add_argument('--host', help='Pi address reachable from Windows; defaults to its .local hostname')
    args = p.parse_args()
    # sudo reads the root-only token. The export belongs to the user invoking this script.
    result = subprocess.run(['sudo','cat','/etc/seedsow-input.json'], check=True, capture_output=True, text=True)
    config = json.loads(result.stdout)
    output = args.output.expanduser()
    with open(output, 'w', encoding='utf-8', opener=lambda name, flags:os.open(name, flags, 0o600)) as f:
        json.dump({'host':args.host or socket.gethostname()+'.local', 'port':config['port'],
                   'token':config['token']}, f, indent=2)
        f.write('\n')
    os.chmod(output, 0o600)
    print('Private connection file saved to '+str(output))
    print('Copy it to Windows, then choose Import connection file in the PC app.')


if __name__ == '__main__':
    main()
