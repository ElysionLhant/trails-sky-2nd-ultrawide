#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_patterns.py - verify that the SUWSF.ini byte patterns still match an exe.

Usage:
    python check_patterns.py [exe] [ini]

Defaults: sora_2nd.exe and SUWSF.ini next to this script.
Tip: if the exe was already patched statically, check the pristine backup:
    python check_patterns.py sora_2nd.exe.bak

Exit code: 0 if every enabled patch matches, 1 otherwise.
"""

import os
import re
import sys

DEFAULT_EXE = "sora_2nd.exe"
DEFAULT_INI = "SUWSF.ini"


def read_patches(ini_path):
    """Minimal parser for [Patch:*] sections (Enabled / Pattern / Offset / Match)."""
    patches = []
    current = None
    with open(ini_path, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line[0] in ";#":
                continue
            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1].strip()
                current = None
                if "Patch" in name:
                    current = {"name": name, "enabled": True,
                               "pattern": None, "offset": 0, "match": "all"}
                    patches.append(current)
                continue
            if current is None or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"')
            if key == "Enabled":
                current["enabled"] = (val.lower() == "true")
            elif key == "Pattern":
                current["pattern"] = val
            elif key == "Offset":
                try:
                    current["offset"] = int(val)
                except ValueError:
                    current["offset"] = -1
            elif key == "Match":
                current["match"] = val
    return patches


def pattern_to_regex(pattern):
    parts = pattern.split()
    rx = b"".join(
        b"." if p in ("??", "?") else re.escape(bytes.fromhex(p))
        for p in parts
    )
    return re.compile(rx, re.DOTALL)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    exe = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, DEFAULT_EXE)
    ini = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, DEFAULT_INI)
    exe = os.path.abspath(exe)
    ini = os.path.abspath(ini)

    if not os.path.exists(exe):
        sys.exit("exe not found: %s" % exe)
    if not os.path.exists(ini):
        sys.exit("ini not found: %s" % ini)

    data = open(exe, "rb").read()
    print("exe : %s (%d bytes)" % (exe, len(data)))
    print("ini : %s" % ini)
    print()

    ok = True
    for p in read_patches(ini):
        if not p["enabled"]:
            print("[skip] %-22s (disabled)" % p["name"])
            continue
        if not p["pattern"]:
            print("[FAIL] %-22s no Pattern in ini" % p["name"])
            ok = False
            continue

        matches = len(pattern_to_regex(p["pattern"]).findall(data))

        need = 1
        if p["match"] not in ("all", "last", "end") and p["match"].isdigit():
            need = max(1, int(p["match"]))

        if matches < need:
            ok = False
            status = "FAIL"
        else:
            status = "OK"

        print("[%s] %-22s matches=%-3d (need>=%d, offset=%d, match=%s)"
              % (status, p["name"], matches, need, p["offset"], p["match"]))

    print()
    if ok:
        print("All enabled patches match -- SUWSF.ini is compatible with this exe.")
    else:
        print("Some patterns do NOT match.")
        print("Hint: if this exe was already patched statically, check the pristine")
        print("      backup instead (sora_2nd.exe.bak); otherwise the game probably")
        print("      updated and the patterns need re-deriving.")
        sys.exit(1)


if __name__ == "__main__":
    main()
