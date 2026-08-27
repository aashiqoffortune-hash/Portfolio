#!/usr/bin/env python3
"""Prove the page ground cannot have broken any text.

    python3 tools/check_ground.py        # non-zero exit if it fails

The ground in style.css is drawn — gradients, not an image — so there is no
file to measure. Instead the layer is rendered on its own in a real browser,
with all content hidden, and its extreme pixels are read back out of the
screenshot. Those extremes are then put against every text token.

Rendering it rather than reasoning about the CSS is deliberate: the answer
that matters is what the browser composites, not what the stylesheet says it
should. If the brightest and darkest pixel the ground can produce are both
safe, every pixel between them is too.
"""

import io
import re
import sys

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

CSS = "static/css/style.css"
URL = "http://127.0.0.1:8899/Portfolio/index.html"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Tokens used as text, and the threshold each must clear. --ink-4 is the
# oversized ghost numeral, only ever set at 3.2rem, so "large text" applies.
TEXT_TOKENS = {
    "--bone": 4.5, "--bone-2": 4.5, "--bone-3": 4.5,
    "--sig-lift": 4.5, "--brass": 4.5, "--ink-4": 3.0,
}

# Viewports worth probing: the gradients are sized in % and vw, so the bloom
# lands differently on a phone than on a wide desktop.
SIZES = [(390, 844), (768, 1024), (1440, 900), (2560, 1440)]


def srgb_to_linear(c):
    c = np.asarray(c, dtype=float) / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(rgb):
    lin = srgb_to_linear(rgb)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def contrast(a, b):
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def tokens():
    css = open(CSS).read()
    out = {}
    for sel, body in re.findall(r"(:root[^{]*)\{([^}]*)\}", css):
        sel = sel.strip()
        name = "light" if sel == ":root" else ("dark" if "dark" in sel else None)
        if name and name not in out:
            out[name] = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body))
    out["dark"] = {**out["light"], **out["dark"]}
    return out


# Hide everything except the ground, so the screenshot is the layer alone.
STRIP = """() => {
  const s = document.createElement('style');
  s.textContent = `.rail,.bar,.column,.skip{display:none!important}
                   body{background:transparent!important}`;
  document.head.appendChild(s);
}"""


def main():
    th = tokens()
    failures = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME)
        for theme in ("light", "dark"):
            lo, hi = 1.0, 0.0
            for w, h in SIZES:
                pg = br.new_page(viewport={"width": w, "height": h},
                                 color_scheme=theme)
                pg.goto(URL)
                pg.evaluate(STRIP)
                pg.wait_for_timeout(250)
                px = np.asarray(Image.open(io.BytesIO(pg.screenshot()))
                                .convert("RGB"), dtype=float)
                gl = luminance(px)
                lo, hi = min(lo, float(gl.min())), max(hi, float(gl.max()))
                pg.close()

            print(f"\n{theme.upper()}  ground luminance over "
                  f"{len(SIZES)} viewports: {lo:.5f} .. {hi:.5f}")
            print(f"  {'token':12} {'flat':>7} {'worst':>7} {'need':>6}   verdict")
            flat = luminance(hex_rgb(th[theme]["--ink"]))
            for name, need in TEXT_TOKENS.items():
                tl = luminance(hex_rgb(th[theme][name]))
                base = contrast(tl, flat)
                worst = min(contrast(tl, lo), contrast(tl, hi))
                if worst < need:
                    failures.append((theme, name, worst, need))
                print(f"  {name:12} {base:7.2f} {worst:7.2f} {need:6.1f}   "
                      f"{'PASS' if worst >= need else 'FAIL'}  "
                      f"({worst - base:+.2f} vs flat)")
        br.close()

    print()
    if failures:
        for theme, name, worst, need in failures:
            print(f"FAIL  {theme} {name}: {worst:.2f} < {need}")
        print("\nThe ground is making text unreadable. Soften --g-scan, "
              "--g-band or --g-glow for that theme in style.css.")
        return 1
    print("Every text token clears WCAG AA against the brightest and darkest "
          "pixel the ground can produce, in both themes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
