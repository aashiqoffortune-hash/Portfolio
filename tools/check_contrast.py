#!/usr/bin/env python3
"""Prove the background cannot have broken any text on the site.

    python3 tools/check_contrast.py          # exits non-zero if it fails

A background image behind text can only hurt legibility in one way: by making
the ground brighter than light-on-dark text can survive, or darker than
dark-on-light text can survive. So the check is not a spot sample — it takes
the *extreme* pixel of each shipped image, blends it with that theme's scrim
exactly as the browser will, and measures every text token against it. If the
worst pixel in the image is safe, every pixel is.

Everything is read back out of style.css and the image files, so this measures
what actually ships rather than what was intended.
"""

import re
import sys

import numpy as np
from PIL import Image

CSS = "static/css/style.css"

# Tokens used as text, and the WCAG threshold each has to clear. --ink-4 is
# the oversized ghost numeral behind a section index — it is only ever set at
# 3.2rem, which is "large text", so 3:1 applies. Every other token is body
# copy or smaller and needs the full 4.5:1.
TEXT_TOKENS = {
    "--bone": 4.5, "--bone-2": 4.5, "--bone-3": 4.5,
    "--sig-lift": 4.5, "--brass": 4.5, "--ink-4": 3.0,
}


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


def blocks(css):
    """The three token blocks: bare :root is light, the other two are dark."""
    out = {}
    for sel, body in re.findall(r"(:root[^{]*)\{([^}]*)\}", css):
        sel = sel.strip()
        name = "light" if sel == ":root" else ("dark" if "dark" in sel else None)
        if name and name not in out:
            out[name] = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body))
    return out


def themes_from_css():
    """Both token sets, with dark's inheritance from light already resolved."""
    themes = blocks(open(CSS).read())
    themes["dark"] = {**themes["light"], **themes["dark"]}
    return themes


def main():
    themes = themes_from_css()

    failures = []
    for theme in ("light", "dark"):
        tok = themes[theme]
        photo = re.search(r'url\("([^"]+)"\)', tok.get("--bg-photo", "")).group(1)
        path = "static/" + photo.split("../", 1)[-1]
        r, g, b, alpha = [float(x) for x in
                          re.findall(r"[\d.]+", tok["--bg-scrim"])]

        img = np.asarray(Image.open(path).convert("RGB"), dtype=float)
        ground = alpha * np.array([r, g, b]) + (1 - alpha) * img
        gl = luminance(ground)
        lo, hi = float(gl.min()), float(gl.max())

        print(f"\n{theme.upper()}  {path}  scrim alpha {alpha}")
        print(f"  ground luminance across every pixel: {lo:.5f} .. {hi:.5f}")
        print(f"  {'token':12} {'flat':>7} {'worst':>7} {'need':>6}   verdict")
        flat_l = luminance(hex_rgb(tok["--ink"]))
        for name, need in TEXT_TOKENS.items():
            tl = luminance(hex_rgb(tok[name]))
            flat = contrast(tl, flat_l)
            worst = min(contrast(tl, lo), contrast(tl, hi))
            ok = worst >= need
            if not ok:
                failures.append((theme, name, worst, need))
            print(f"  {name:12} {flat:7.2f} {worst:7.2f} {need:6.1f}   "
                  f"{'PASS' if ok else 'FAIL'}  ({worst - flat:+.2f} vs flat)")

    print()
    if failures:
        for theme, name, worst, need in failures:
            print(f"FAIL  {theme} {name}: {worst:.2f} < {need}")
        print("\nThe background is making text unreadable. Either raise the scrim "
              "alpha in style.css, or re-run tools/make_backgrounds.py with a "
              "narrower window.")
        return 1
    print("All text tokens clear WCAG AA against the worst pixel of the "
          "background, in both themes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
