#!/usr/bin/env python3
"""Fail if anything vendor-identifiable reached the published site.

    python3 tools/check_sanitised.py [build_dir]

The case study is a written sample against an invented environment. This
checks that it stayed that way — that no lab hostname, vendor name, real
credential, proving-grounds address range or flag format is anywhere in the
built output, including inside the JavaScript and the stylesheet.

It is deliberately blunt. A false positive costs a rename; a false negative
puts a rules violation on a portfolio used to get hired in security.
"""

import re
import sys
from pathlib import Path

# Names, ranges and formats that must never appear. Kept as patterns rather
# than a list of the specific machines, so this keeps working for whatever
# gets written next.
FORBIDDEN = [
    (r"(?i)\boffsec\b", "vendor name"),
    # "offensive security" on its own is the discipline and the job title, and
    # appears all over the site legitimately. The vendor is caught by its
    # abbreviation above and by its platform and certification names below.
    (r"(?i)\bproving\s*grounds?\b", "vendor platform"),
    (r"(?i)\bPG\s*(?:play|practice)\b", "vendor platform"),
    (r"(?i)\b(?:oscp|osep|oswe|osed|exam\s+machine)\b", "vendor certification/exam"),
    (r"(?i)\bhutch\b", "lab hostname"),
    (r"(?i)\bauthby\b", "lab hostname"),
    (r"(?i)\bfmcsorley\b", "lab account"),
    (r"CrabSharkJellyfish", "lab credential"),
    (r"(?i)\brockyou\b", "lab-adjacent artefact"),
    (r"(?i)ms-MCS-AdmPwd", "lab-specific attribute"),
    # the proving-grounds VPN ranges these reports were captured on
    (r"\b192\.168\.(?:4[0-9]|1[0-9][0-9]|2[0-9][0-9])\.\d{1,3}\b", "lab VPN address"),
    # flag / proof formats
    (r"(?i)\b(?:local|proof)\.txt\b", "flag file"),
    (r"\b[0-9a-f]{32}\b", "possible proof hash"),
]

# The NT hash of the empty string. It is a published constant that appears in
# every pass-the-hash reference, and the salvo terminal uses it as its sample
# hash precisely because it discloses nothing.
ALLOWED_HASHES = {"31d6cfe0d16ae931b73c59d7e0c089c0"}

# Addresses the site is allowed to use: the salvo terminal's invented estate
# and the case study's RFC 1918 examples.
ALLOWED_ADDR = re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.(?:100|1)\.\d{1,3})\b")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "build")
    if not root.is_dir():
        print(f"  FAIL  {root} does not exist")
        return 1

    files = [p for p in root.rglob("*")
             if p.is_file() and p.suffix in {".html", ".css", ".js", ".txt", ".json", ".svg"}]
    print(f"scanning {len(files)} text files under {root}")

    hits = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, why in FORBIDDEN:
            for m in re.finditer(pattern, text):
                if m.group().lower() in ALLOWED_HASHES:
                    continue
                frag = text[max(0, m.start() - 45):m.end() + 45].replace("\n", " ")
                print(f"  FAIL  {path.relative_to(root)}: {why} — "
                      f"{m.group()!r}\n         …{frag.strip()}…")
                hits += 1

    print()
    if hits:
        print(f"{hits} problem(s). Nothing here should be published.")
        return 1
    print("No vendor name, lab hostname, lab credential, lab address range or "
          "flag format anywhere in the built site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
