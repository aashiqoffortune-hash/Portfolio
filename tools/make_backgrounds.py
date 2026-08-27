#!/usr/bin/env python3
"""Turn the source photograph into the two page backgrounds.

    python3 tools/make_backgrounds.py

The constraint this exists to satisfy is not aesthetic. Every text colour on
the site clears WCAG AA against the flat token ground; a background image can
only ever break that by making the ground brighter (dark theme) or darker
(light theme) than the text can survive. Solving for the dimmest normal-weight
token on each theme gives a hard window:

    dark    the ground may never exceed 8-bit ~37
    light   the ground may never fall below 8-bit ~238

The naive approach — drop the photo in and wash it out with a heavy scrim —
spends that window badly: it throws away the photograph's structure and keeps
its brightness. So instead the photo is tone-mapped *into* the window. Every
star, the tent, the horizon lights and the rocks all survive, at low
amplitude, and the ground is inside the safe band by construction rather than
by a scrim tuned until it looked fine.

Luminance is remapped and the per-pixel scale is applied to all three
channels, so hue and relative saturation are preserved: the tent stays orange
against a blue sky instead of drifting grey.

tools/check_contrast.py re-derives the guarantee from the shipped files and
fails loudly if it ever stops holding.
"""

import numpy as np
from PIL import Image

from check_contrast import TEXT_TOKENS, contrast, hex_rgb, luminance, themes_from_css

SOURCE = "assets/camp-source.jpg"
OUT_W, OUT_H = 1920, 1200          # 16:10 — close to the common viewport, so
                                   # background-size:cover crops very little

# How much better than the bare WCAG threshold every pair has to land. The
# window is solved for this, not chosen: pick the margin, and the brightness
# the photograph is allowed to reach follows from the text colours themselves.
#
# 1.05 is not timidity, it is what this palette can afford. Two tokens sit
# close to their thresholds on a flat ground before any image exists —
# --bone-3 on light is 5.20 against a 4.5 requirement, and --ink-4 on dark is
# 3.41 against 3.0 — so roughly 13% of headroom is all there is to spend.
# Asking for 15% makes the light theme infeasible outright: the solver runs
# the floor past pure white and hands back a blank image.
MARGIN = 1.05

# The shape of the two window ends. Only the scale is solved; these ratios set
# the white point. The dark end is warm because the tent's core is blown to
# white in the source, and a neutral ceiling renders it a grey-green chip in
# the middle of an orange glow. A warm ceiling keeps it an ember.
DARK_TINT = np.array([1.00, 0.84, 0.66])     # amber highlight
DARK_FLOOR = np.array([1.0, 1.0, 2.0])       # a hair of blue left in the shadows
LIGHT_TINT = np.array([1.00, 0.97, 0.90])    # what gets subtracted from white
LIGHT_CEIL = np.array([255.0, 255.0, 255.0])


def solve_window(theme_tokens, scrim_rgb, alpha, tint, dark):
    """How bright may the image get before the text stops clearing AA?

    Solved rather than picked. Every text token gives a cap on the ground
    luminance; the tightest one wins; then the scrim is inverted to turn that
    ground cap into a cap on the image itself. Bisection because luminance is
    not linear in the 8-bit values being solved for.
    """
    caps = []
    for name, need in TEXT_TOKENS.items():
        tl = luminance(hex_rgb(theme_tokens[name]))
        target = need * MARGIN
        if dark:                       # ground must stay BELOW this
            caps.append((tl + 0.05) / target - 0.05)
        else:                          # ground must stay ABOVE this
            caps.append(target * (tl + 0.05) - 0.05)
    cap = min(caps) if dark else max(caps)

    def ground_lum(k):
        end = tint * k if dark else 255.0 - tint * k
        return luminance(alpha * np.asarray(scrim_rgb) + (1 - alpha) * end)

    # Infeasible means the margin asked for more headroom than the palette has.
    # Say so, rather than returning a flat image and calling it a background.
    if (ground_lum(0.0) > cap) if dark else (ground_lum(0.0) < cap):
        raise SystemExit(
            f"MARGIN={MARGIN} is unreachable on the {'dark' if dark else 'light'} "
            f"theme: even a flat ground misses the required {cap:.5f}. Lower "
            f"MARGIN, or lighten the text tokens that sit closest to their "
            f"thresholds.")

    lo, hi = 0.0, 255.0
    for _ in range(60):                # 60 halvings is exact to well under a level
        mid = (lo + hi) / 2
        too_far = ground_lum(mid) > cap if dark else ground_lum(mid) < cap
        if too_far:
            hi = mid
        else:
            lo = mid
    return tint * lo, cap


def load():
    """Crop to 16:10 without losing the tent.

    The source is 4:3. The bottom of the frame is unlit foreground and the top
    is empty sky, so the crop is taken slightly above centre: that keeps the
    horizon, the tent and its pool of light, and drops the least interesting
    band of shadow.
    """
    im = Image.open(SOURCE).convert("RGB")
    w, h = im.size
    want_h = int(round(w * OUT_H / OUT_W))
    top = int((h - want_h) * 0.42)          # bias the crop upward
    im = im.crop((0, top, w, top + want_h))
    return im.resize((OUT_W, OUT_H), Image.LANCZOS)


def luma(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def tone_map(a, floor, ceil, gamma, sat):
    """Compress the photograph into [floor, ceil] with its structure intact.

    Every channel is put through the same monotone curve straight into the
    window, so the result is inside it by construction — luminance is a convex
    combination of the channels, and if no channel can leave the window then
    neither can the luminance. That matters more than it sounds: the obvious
    alternative, scaling each pixel by the ratio of its target luminance to
    its actual one, has unbounded gain wherever the source is near black, and
    on a night photograph that means amplifying sensor noise into coloured
    blotches across the whole foreground.

    The curve is contractive everywhere — the window is far narrower than the
    source range — so it suppresses that noise instead.

    `gamma` below 1 opens the midtones before the squeeze, which is what keeps
    the rocks, the sea and the sky from collapsing into one another. `sat`
    restores the colourfulness that compressing into ~35 levels costs, applied
    before the curve so it cannot push anything out of the window.
    """
    L = luma(a)[..., None]
    out = np.clip(L + (a - L) * sat, 0, 255)

    n = (out / 255.0).clip(0, 1)
    if float(ceil.max()) <= 128:         # dark theme: pull down into 0..ceil
        out = floor + (n ** gamma) * (ceil - floor)
    else:                                # light theme: lift up into floor..255
        out = ceil - ((1 - n) ** gamma) * (ceil - floor)
    return np.clip(out, 0, 255)


def report(name, arr):
    L = luma(arr)
    print(f"  {name:22} 8-bit luminance {L.min():5.1f} .. {L.max():5.1f}"
          f"   mean {L.mean():5.1f}")


if __name__ == "__main__":
    import os, re
    photo = np.asarray(load(), dtype=np.float32)
    os.makedirs("static/img", exist_ok=True)

    th = themes_from_css()
    def scrim(t):
        r, g, b, a = [float(x) for x in re.findall(r"[\d.]+", th[t]["--bg-scrim"])]
        return [r, g, b], a

    d_rgb, d_a = scrim("dark")
    l_rgb, l_a = scrim("light")
    dark_ceil, d_cap = solve_window(th["dark"], d_rgb, d_a, DARK_TINT, dark=True)
    light_sub, l_cap = solve_window(th["light"], l_rgb, l_a, LIGHT_TINT, dark=False)
    light_floor = LIGHT_CEIL - light_sub

    print(f"  solved window (margin x{MARGIN})")
    print(f"    dark  ceiling {np.round(dark_ceil, 1)}   ground cap L<={d_cap:.5f}")
    print(f"    light floor   {np.round(light_floor, 1)}   ground floor L>={l_cap:.5f}")

    dark = tone_map(photo, DARK_FLOOR, dark_ceil, gamma=0.60, sat=1.35)
    light = tone_map(photo, light_floor, LIGHT_CEIL, gamma=0.85, sat=1.20)

    for arr, path, q in ((dark, "static/img/bg-dark.webp", 90),
                         (light, "static/img/bg-light.webp", 92)):
        Image.fromarray(arr.astype(np.uint8), "RGB").save(path, quality=q, method=6)
        report(os.path.basename(path), np.asarray(Image.open(path), dtype=np.float32))
        print(f"  {'':22} {os.path.getsize(path)/1024:.1f} KB")
