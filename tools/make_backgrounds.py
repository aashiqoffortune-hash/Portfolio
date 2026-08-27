#!/usr/bin/env python3
"""Generate the two page backgrounds.

They are committed as images, so this only needs running when the look
changes — but it is kept in the repo because a background nobody can
regenerate is a background nobody can adjust.

The brief is narrow. The background has to carry depth without carrying
attention: every text/ground pair on the site clears WCAG AA against the
flat token colour, and the image must not move any of them. So the
amplitude is deliberately tiny, the scrim in style.css does most of the
work, and the result is verified by re-measuring contrast on the built
pages rather than by eye.

    python3 tools/make_backgrounds.py
"""

import numpy as np
from PIL import Image, ImageFilter

W, H = 1920, 1200
rng = np.random.default_rng(20260827)      # fixed: the build is reproducible


def octave(w, h, cells, blur):
    """One band of smooth low-frequency variation, in 0..1."""
    small = rng.random((cells, max(1, int(cells * h / w)))).astype(np.float32)
    img = Image.fromarray((small.T * 255).astype(np.uint8), "L")
    img = img.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(img, dtype=np.float32) / 255.0
    return (a - a.mean()) / (a.std() + 1e-6)


def field():
    """Several octaves stacked — the organic, uneven falloff a photograph of
    a surface has and a CSS gradient never does."""
    f = (1.00 * octave(W, H, 3, 90) +
         0.55 * octave(W, H, 7, 45) +
         0.28 * octave(W, H, 17, 18) +
         0.13 * octave(W, H, 41, 7))
    return (f - f.mean()) / (f.std() + 1e-6)


def vignette(strength):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    x = (x - W / 2) / (W / 2)
    y = (y - H / 2) / (H / 2)
    r = np.sqrt(x * x + y * y) / np.sqrt(2)
    return 1.0 - strength * (r ** 1.7)


def build(base_rgb, amp, grain, vig, warm, out, quality):
    """base_rgb  the token colour this sits behind
       amp       luminance swing, in 0..255 — keep small
       grain     per-pixel noise amplitude
       vig       corner falloff
       warm      how much redder the lit areas are than the dark ones
    """
    f = field()
    lum = np.clip(f, -2.2, 2.2) * amp
    v = vignette(vig)

    px = np.empty((H, W, 3), dtype=np.float32)
    for i, base in enumerate(base_rgb):
        # the warm channel lifts with the light, the cool one lags: a flat
        # tint reads as a colour wash, this reads as a surface
        tilt = warm * (1.0 - i * 0.5)
        px[:, :, i] = (base + lum * (1.0 + tilt)) * v

    px += rng.normal(0.0, grain, (H, W, 3)).astype(np.float32)
    img = Image.fromarray(np.clip(px, 0, 255).astype(np.uint8), "RGB")
    img.save(out, quality=quality, method=6)
    return out


if __name__ == "__main__":
    import os
    made = [
        # dark: the warm near-black ground, lit unevenly from the upper left
        build((16, 18, 22), amp=7.0, grain=1.5, vig=0.30, warm=0.35,
              out="static/img/bg-dark.webp", quality=88),
        # light: paper under a window. Far subtler — dark text on a light
        # ground shows any mottling far more readily.
        build((250, 249, 247), amp=3.4, grain=0.9, vig=0.10, warm=0.25,
              out="static/img/bg-light.webp", quality=90),
    ]
    for p in made:
        print("%-28s %6.1f KB" % (p, os.path.getsize(p) / 1024))
