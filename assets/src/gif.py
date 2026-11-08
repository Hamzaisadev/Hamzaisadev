"""Raymarch an extruded 'H', light it, Bayer-dither to 3 colours, write a looping GIF per theme."""
import numpy as np
from PIL import Image
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 360   # output px
S = N // 2                                              # render res (upscaled 2x => chunky dither)
FRAMES = 72

THEMES = {"light": ((0xF3, 0xEF, 0xE7), (0x14, 0x13, 0x11), (0xFF, 0x4A, 0x1C)),
          "dark":  ((0x0E, 0x0E, 0x0D), (0xEE, 0xE9, 0xDF), (0xFF, 0x5A, 0x2E))}


def bayer(n):
    m = np.array([[0, 2], [3, 1]])
    while m.shape[0] < n:
        m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + .5) / m.size


def sd_box(p, c, b):
    q = np.abs(p - c) - b
    return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.max(q, axis=-1), 0)


def sdf(p):
    d = 0.16
    a = sd_box(p, np.array([-.42, 0, 0]), np.array([.13, .62, d]))
    b = sd_box(p, np.array([.42, 0, 0]), np.array([.13, .62, d]))
    c = sd_box(p, np.array([0, .02, 0]), np.array([.32, .11, d]))
    return np.minimum(np.minimum(a, b), c) - .035   # rounded edges


def rot(t):
    cy, sy = np.cos(t), np.sin(t)
    tilt = .32
    cx, sx = np.cos(tilt), np.sin(tilt)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    return Rx @ Ry


def render(t):
    R = rot(t)
    u = np.linspace(-1.05, 1.05, S)
    X, Y = np.meshgrid(u, -u)
    ro = np.array([0, 0, 3.2])
    rd = np.stack([X, Y - .05, -np.full_like(X, 2.6)], -1)
    rd /= np.linalg.norm(rd, axis=-1, keepdims=True)
    tt = np.zeros(X.shape)
    hit = np.zeros(X.shape, bool)
    for _ in range(70):
        p = (ro + rd * tt[..., None]) @ R          # object space
        d = sdf(p)
        hit |= d < 1e-3
        tt = np.where(hit, tt, tt + d * .9)
    p = (ro + rd * tt[..., None]) @ R
    e = 2e-3
    n = np.stack([sdf(p + np.array(v)) - sdf(p - np.array(v)) for v in ([e, 0, 0], [0, e, 0], [0, 0, e])], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    n = n @ R.T                                       # back to world
    L = np.array([-.45, .55, .8]); L /= np.linalg.norm(L)
    diff = np.clip((n * L).sum(-1), 0, 1)
    h = L - rd; h /= np.linalg.norm(h, axis=-1, keepdims=True)
    spec = np.clip((n * h).sum(-1), 0, 1) ** 40
    shade = np.clip(.12 + .85 * diff + .6 * spec, 0, 1)
    # floor shadow ellipse
    fy = .78
    ground = np.exp(-(((X) / (.62 + .1 * abs(np.sin(t)))) ** 2 + ((Y + fy) / .07) ** 2) * 2.2)
    return hit, shade, ground


def frames(theme):
    paper, ink, acc = THEMES[theme]
    B = np.tile(bayer(8), (S // 8 + 1, S // 8 + 1))[:S, :S]
    pal = [*paper, *ink, *acc] + [0] * (256 * 3 - 9)
    out = []
    for f in range(FRAMES):
        t = 2 * np.pi * f / FRAMES
        hit, shade, ground = render(t)
        idx = np.zeros((S, S), np.uint8)                         # paper
        idx[(~hit) & (ground * .55 > B)] = 1                     # dithered ink shadow
        idx[hit] = np.where(shade > B, 2, 1)[hit]                # lit = accent, dark = ink
        im = Image.fromarray(idx, "P")
        im.putpalette(pal)
        out.append(im.resize((N, N), Image.NEAREST))
    return out


for th in THEMES:
    fr = frames(th)
    fr[0].save(f"{sys.argv[2] if len(sys.argv) > 2 else 'out'}/monogram-{th}.gif", save_all=True, append_images=fr[1:],
               duration=50, loop=0, optimize=False, disposal=1)
print("ok")
