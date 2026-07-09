"""
Generate icon.ico for the Fabric Weight Calculator using ONLY the Python
standard library (zlib + struct). No Pillow / no extra installs needed.

Draws a rolled bolt of fabric on the app's blue gradient background,
supersampled for smooth (anti-aliased) edges, and packs several sizes
(256/64/48/32/16) into a single Windows .ico file.
"""

import zlib
import struct
import math
import os

# ---- geometry (as fractions of the canvas) -------------------------------
CY = 0.45      # cylinder vertical center
X0 = 0.18      # left edge of roll body
X1 = 0.64      # right end of roll body (center of end-cap disc)
RY = 0.205     # cylinder half-height
CAP_RX = 0.095 # end-cap disc horizontal radius

# ---- colors --------------------------------------------------------------
BG_TOP = (36, 122, 205)
BG_BOT = (6, 42, 80)
BODY = (244, 236, 220)
CAP = (223, 209, 184)
DRAPE = (236, 226, 205)


def lerp(a, b, t):
    return a + (b - a) * t


def rounded_rect(x, y, w, h, r):
    """True if point (x,y) is inside a w*h rounded rect with corner radius r."""
    if x < 0 or y < 0 or x > w or y > h:
        return False
    cx = min(max(x, r), w - r)
    cy = min(max(y, r), h - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def scene_color(px, py, N):
    """Return (r,g,b,a) for a point in an N*N canvas (float coords)."""
    x, y = px / N, py / N  # normalized 0..1

    # outside rounded background -> transparent
    r_corner = 0.20
    if not rounded_rect(x, y, 1.0, 1.0, r_corner):
        return (0, 0, 0, 0)

    # --- background vertical gradient ---
    t = y
    col = [lerp(BG_TOP[i], BG_BOT[i], t) for i in range(3)]

    # --- soft shadow beneath the roll ---
    sx, sy, srx, sry = (X0 + X1) / 2 + 0.02, CY + RY + 0.06, 0.30, 0.06
    sd = ((x - sx) / srx) ** 2 + ((y - sy) / sry) ** 2
    if sd < 1.0:
        f = 1.0 - 0.45 * (1.0 - sd)  # darker toward shadow center
        col = [c * f for c in col]

    # --- roll body (cylinder) ---
    if X0 <= x <= X1 and abs(y - CY) <= RY:
        tt = (y - CY) / RY  # -1 (top) .. 1 (bottom)
        shade = 1.0 - 0.10 * max(0, tt) ** 1.5 - 0.30 * max(0, tt) - 0.18 * max(0, -tt)
        shade = 1.06 - 0.30 * abs(tt + 0.15)  # highlight slightly above center
        col = [min(255, c * shade) for c in BODY]
        # thin darker rim on the left cut edge for depth
        if x <= X0 + 0.02:
            col = [c * 0.8 for c in col]

    # --- rolled end-cap disc (spiral) on the right ---
    nx = (x - X1) / CAP_RX
    ny = (y - CY) / RY
    d = math.sqrt(nx * nx + ny * ny)
    if d <= 1.0:
        ang = math.atan2(ny, nx)
        spiral = math.sin(d * (2 * math.pi * 5.0) + ang)  # concentric rolled layers
        shade = 0.88 + 0.14 * spiral
        if d > 0.92:
            shade *= 0.8  # dark outer rim
        col = [min(255, c * shade) for c in CAP]

    # --- fabric draping down from the lower front ---
    dw = 0.30
    dtop = CY + RY * 0.25
    if X0 <= x <= X0 + dw:
        wave = 0.035 * math.sin((x - X0) / dw * 2 * math.pi * 1.5)
        dbot = CY + RY + 0.16 + wave
        if dtop <= y <= dbot:
            folds = 0.9 + 0.12 * math.sin((x - X0) / dw * 2 * math.pi * 4)
            vgrad = 1.0 - 0.18 * (y - dtop) / (dbot - dtop)
            col = [min(255, c * folds * vgrad) for c in DRAPE]

    return (int(col[0]), int(col[1]), int(col[2]), 255)


def render(size, ss=3):
    """Render an anti-aliased size*size RGBA image (bytes) via supersampling."""
    hi = size * ss
    # render high-res
    hires = bytearray(hi * hi * 4)
    for j in range(hi):
        for i in range(hi):
            r, g, b, a = scene_color(i + 0.5, j + 0.5, hi)
            o = (j * hi + i) * 4
            hires[o:o + 4] = bytes((r, g, b, a))
    # box-downsample by ss
    out = bytearray(size * size * 4)
    n = ss * ss
    for j in range(size):
        for i in range(size):
            sr = sg = sb = sa = 0
            for dy in range(ss):
                for dx in range(ss):
                    o = ((j * ss + dy) * hi + (i * ss + dx)) * 4
                    sr += hires[o]; sg += hires[o + 1]
                    sb += hires[o + 2]; sa += hires[o + 3]
            o = (j * size + i) * 4
            out[o:o + 4] = bytes((sr // n, sg // n, sb // n, sa // n))
    return bytes(out)


def make_png(size, rgba):
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    raw = bytearray()
    stride = size * 4
    for y in range(size):
        raw.append(0)
        raw.extend(rgba[y * stride:(y + 1) * stride])
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def make_ico(sizes, out_path):
    pngs = []
    for s in sizes:
        print(f"  rendering {s}x{s} ...")
        pngs.append((s, make_png(s, render(s))))
    n = len(pngs)
    header = struct.pack("<HHH", 0, 1, n)
    entries = b""
    offset = 6 + 16 * n
    for s, data in pngs:
        w = h = 0 if s >= 256 else s
        entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    with open(out_path, "wb") as f:
        f.write(header + entries + b"".join(d for _, d in pngs))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    project = "/Users/taimuradam/Documents/GitHub/gsm-calculations"
    # multi-size .ico for Windows
    make_ico([256, 64, 48, 32, 16], os.path.join(project, "icon.ico"))
    # a preview PNG so we can eyeball it
    with open(os.path.join(here, "preview.png"), "wb") as f:
        f.write(make_png(256, render(256)))
    print("Wrote preview.png")
