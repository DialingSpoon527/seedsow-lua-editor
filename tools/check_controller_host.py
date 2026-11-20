#!/usr/bin/env python3
"""Report Linux controller-host prerequisites without pairing or changing settings."""

import importlib.metadata
import json
import platform
import re
import subprocess


def bluetoothctl(*args):
    try:
        result = subprocess.run(
            ["bluetoothctl", *args], capture_output=True, text=True, timeout=5
        )
    except FileNotFoundError:
        return "not installed", ""
    except subprocess.TimeoutExpired:
        return "timed out", ""
    except OSError:
        return "could not run", ""
    if result.returncode:
        return "command failed", ""
    return "ok", result.stdout


def package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def main():
    system = platform.system()
    report = {
        "os": system,
        "python": platform.python_version(),
        "python_environment_packages": {
            name: package_version(name) for name in ("nxbt", "nuxbt")
        },
    }
    if system == "Linux":
        status, output = bluetoothctl("--version")
        match = re.search(r"\b\d+\.\d+(?:\.\d+)?\b", output)
        report["bluez"] = {"status": status, "version": match[0] if match else None}
        status, output = bluetoothctl("list")
        report["adapters"] = {
            "status": status,
            "count": sum(line.lstrip().startswith("Controller ") for line in output.splitlines())
            if status == "ok" else None,
        }
    else:
        report["bluez"] = {"status": "check on the Linux Bluetooth host"}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
