#!/usr/bin/env python3
"""Read-only DDOS custody check. No dependencies, credentials, or ledger writes."""
import argparse
import json
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

REQUIRED = ("SOUL.md", "AGENTS.md", "HEARTBEAT.md", "MEMORY.md")

def check(root, urls, timeout=8):
    root = pathlib.Path(root)
    files = {name: (root / name).is_file() for name in REQUIRED}
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL, timeout=5
        ).strip()
    except (OSError, subprocess.SubprocessError):
        revision = None
    endpoints = {}
    for url in urls:
        if not url.startswith("https://"):
            endpoints[url] = {"ok": False, "error": "HTTPS required"}
            continue
        try:
            req = urllib.request.Request(url, method="GET", headers={"User-Agent": "DDOS-CustodyCheck/1"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                endpoints[url] = {"ok": 200 <= response.status < 400, "status": response.status}
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            endpoints[url] = {"ok": False, "error": type(exc).__name__}
    return {
        "worker": "Diego Prime", "mode": "read-only", "source_revision": revision,
        "required_files": files, "endpoints": endpoints,
        "custody_files_present": all(files.values()),
        "runtime_certified": False, "ledger_written": False,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent))
    parser.add_argument("--url", action="append", default=[], help="Public HTTPS URL to check; repeatable")
    args = parser.parse_args()
    result = check(args.root, args.url)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["custody_files_present"] and all(x["ok"] for x in result["endpoints"].values()) else 1

if __name__ == "__main__":
    sys.exit(main())
