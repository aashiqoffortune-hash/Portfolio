#!/usr/bin/env python3
"""Smoke-test the frozen site.

    python3 tools/check_build.py [build_dir]

`python freeze.py` exiting zero only means Jinja did not raise. It will
happily write a page with an unresolved variable in it, a link to an asset
that was never copied, or — as happened once — a section whose content
vanished because the data module it read from had been renamed. This checks
the bytes that would actually be published.

No browser: this runs in CI, where there isn't one. Everything here is
checkable from the static output alone.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urldefrag

PAGES = {
    "index.html": [
        "Aashiq Shaikh", "Engagement", "salvo",
    ],
    "salvo/index.html": [
        "Run it", "kali@kali", "LOCKOUT MATH", "NOT A VERDICT",
        "salvo-data", "Claims &amp; evidence",
        # What ships. These are the checkable claims on the page, so a
        # rename in the data that empties the block should fail here
        # rather than quietly publish a case with no install line.
        "pipx install salvo-nxc", "Scope enforced",
    ],
    # The commercial page. Every price is a string in the data rather than
    # anything computed, so the failure this guards against is the section
    # vanishing wholesale — a renamed key rendering an empty grid.
    "engagements/index.html": [
        "Perimeter Review", "Fixed scope", "The deliverable",
        "₹45,000", "₹1,45,000", "₹2,75,000",
        "data-usd", "Straight answers",
    ],
}

# Anything that would mean a template rendered wrong rather than merely oddly.
POISON = ["{{", "{%", "Undefined", "None</", ">None<"]


def fail(msg):
    print(f"  FAIL  {msg}")
    return 1


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "build")
    bad = 0

    if not root.is_dir():
        return fail(f"{root} does not exist — did freeze.py run?")

    print(f"checking {root}")

    for rel, needles in PAGES.items():
        page = root / rel
        if not page.is_file():
            bad += fail(f"{rel} is missing")
            continue
        html = page.read_text(encoding="utf-8")
        if len(html) < 4000:
            bad += fail(f"{rel} is only {len(html)} bytes — page is near-empty")
        for needle in needles:
            if needle not in html:
                bad += fail(f"{rel} lost {needle!r}")
        for poison in POISON:
            if poison in html:
                bad += fail(f"{rel} contains {poison!r} — a template did not render")

        # every local reference has to resolve to a file that was written
        for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
            if ref.startswith(("http://", "https://", "//", "#", "mailto:", "data:")):
                continue
            target = (page.parent / unquote(urldefrag(ref)[0].split("?")[0])).resolve()
            if not target.exists():
                bad += fail(f"{rel} links {ref} → {target} which was not built")

        print(f"  ok    {rel}  ({len(html):,} bytes)")

    # the terminal's data island has to be valid JSON or the engine dies silently
    salvo = root / "salvo/index.html"
    if salvo.is_file():
        m = re.search(r'id="salvo-data">(.*?)</script>', salvo.read_text(), re.S)
        if not m:
            bad += fail("salvo-data island is missing")
        else:
            try:
                data = json.loads(m.group(1))
            except json.JSONDecodeError as exc:
                bad += fail(f"salvo-data is not valid JSON: {exc}")
            else:
                for key in ("estate", "nxc", "verdicts", "examples", "opening", "ps1"):
                    if key not in data:
                        bad += fail(f"salvo-data has no {key!r}")
                hosts = len(data.get("estate", {}).get("hosts", []))
                if hosts < 2:
                    bad += fail(f"estate has {hosts} hosts — the terminal has nothing to answer for")
                else:
                    print(f"  ok    salvo-data  ({hosts} hosts, "
                          f"{len(data.get('examples', []))} examples)")

    # the drawn ground has to survive into the published stylesheet
    css = root / "static/css/style.css"
    if not css.is_file():
        bad += fail("static/css/style.css was not built")
    else:
        text = css.read_text()
        for token in ("--g-scan", "--g-band", "--g-glow", "body::before"):
            if token not in text:
                bad += fail(f"style.css lost {token}")
        print(f"  ok    style.css  ({len(text):,} bytes)")

    print()
    if bad:
        print(f"{bad} problem(s) — this build should not be published.")
        return 1
    print("Build is complete and internally consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
