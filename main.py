"""make.fun news-image entry: draw a one-image summary of 18 Nov 2026 world news.

Zero third-party dependencies: a tiny raster + a hand-rolled PNG encoder + an
embedded 5x7 bitmap font, so it runs on a bare python3.13 sandbox.
"""
import os
import struct
import zlib

W, H = 1600, 900
BG = (12, 16, 24)
PANEL = (22, 28, 40)
INK = (238, 242, 248)
MUTED = (150, 162, 180)
ACCENT = (255, 176, 32)
ACCENT2 = (86, 156, 255)

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000",) * 7,
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
}

canvas = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i] = c[0]
        canvas[i + 1] = c[1]
        canvas[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(max(0, y), min(H, y + h)):
        row = (yy * W) * 3
        for xx in range(max(0, x), min(W, x + w)):
            i = row + xx * 3
            canvas[i] = c[0]
            canvas[i + 1] = c[1]
            canvas[i + 2] = c[2]


def rrect(x, y, w, h, r, c):
    rect(x + r, y, w - 2 * r, h, c)
    rect(x, y + r, w, h - 2 * r, c)
    for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r), (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    px(cx + dx, cy + dy, c)


def circle(cx, cy, r, c, fill=True):
    for dy in range(-r, r + 1):
        span = int((r * r - dy * dy) ** 0.5)
        if fill:
            rect(cx - span, cy + dy, span * 2 + 1, 1, c)
        else:
            px(cx - span, cy + dy, c)
            px(cx + span, cy + dy, c)


def line(x0, y0, x1, y1, c, thick=2):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        for ox in range(thick):
            for oy in range(thick):
                px(x0 + ox, y0 + oy, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def text(x, y, s, c, scale=3, tracking=1):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch)
        if g:
            for ry, row in enumerate(g):
                for rx, bit in enumerate(row):
                    if bit == "1":
                        rect(cx + rx * scale, y + ry * scale, scale, scale, c)
        cx += (5 + tracking) * scale
    return cx


def text_w(s, scale=3, tracking=1):
    return len(s) * (5 + tracking) * scale


def star(cx, cy, r, c):
    for a in range(0, 360, 12):
        rad = a * 3.14159 / 180
        line(cx, cy, int(cx + r * __import__("math").cos(rad)), int(cy + r * __import__("math").sin(rad)), c, 2)


def panel(x, y, w, h, accent):
    rrect(x, y, w, h, 18, PANEL)
    rrect(x, y, w, 6, 3, accent)


def main():
    import math

    rect(0, 0, W, H, BG)
    for i in range(H):  # subtle vertical gradient
        t = i / H
        c = (int(10 + 10 * t), int(14 + 12 * t), int(22 + 18 * t))
        rect(0, i, W, 1, c)

    # header
    text(70, 54, "WORLD NEWS / ONE IMAGE", ACCENT, 3)
    text(70, 100, "WEDNESDAY 18 NOVEMBER 2026", INK, 5)
    rect(70, 170, 1460, 3, (46, 56, 74))

    # globe motif on the right of the header
    gx, gy, gr = 1430, 118, 74
    circle(gx, gy, gr, (40, 70, 110))
    circle(gx, gy, gr - 2, (18, 46, 82))
    for k in range(-3, 4):
        off = int(gr * math.cos(k * 0.32))
        line(gx - off, gy + k * 18, gx + off, gy + k * 18, (60, 110, 170), 1)
    for k in range(1, 4):
        off = int(gr * math.sin(k * 0.5))
        circle(gx, gy, max(6, gr - k * 20), (60, 110, 170), fill=False)

    cards = [
        ("SUMMIT", "US CHINA AND RUSSIA LEADERS SET TO MEET", ACCENT),
        ("ASIA", "JAPAN PM TAKAICHI SPEAKS WITH TRUMP FIRST", ACCENT2),
        ("TECH", "AI AGENTS MOVE FROM DEMOS INTO PAID WORK", (120, 220, 160)),
        ("MARKETS", "CRYPTO STEADY AS RATES STAY HIGH", (230, 120, 180)),
    ]
    cw, ch, gap = 700, 182, 34
    x0, y0 = 70, 220
    for idx, (tag, head, col) in enumerate(cards):
        cx = x0 + (idx % 2) * (cw + gap)
        cy = y0 + (idx // 2) * (ch + gap)
        panel(cx, cy, cw, ch, col)
        text(cx + 28, cy + 28, tag, col, 3)
        # wrap headline
        words = head.split()
        lines, cur = [], ""
        for w_ in words:
            trial = (cur + " " + w_).strip()
            if text_w(trial, 4) > cw - 120:
                lines.append(cur)
                cur = w_
            else:
                cur = trial
        if cur:
            lines.append(cur)
        for li, ln in enumerate(lines[:3]):
            text(cx + 28, cy + 84 + li * 44, ln, INK, 4)
        # icon
        ix, iy = cx + cw - 70, cy + 66
        if idx == 0:
            line(ix - 26, iy, ix + 26, iy, col, 3)
            line(ix, iy - 26, ix, iy + 26, col, 3)
            circle(ix, iy, 26, col, fill=False)
        elif idx == 1:
            rect(ix - 24, iy - 16, 48, 32, col)
            rect(ix - 6, iy - 22, 12, 8, col)
        elif idx == 2:
            for k in range(4):
                rect(ix - 26 + k * 14, iy - 20 + (k % 2) * 10, 10, 30, col)
        else:
            pts = [(-26, 14), (-14, -4), (-2, 8), (10, -16), (24, -6)]
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                line(ix + ax, iy + ay, ix + bx, iy + by, col, 3)

    # also-today ticker band
    band_y = 700
    rrect(70, band_y, 1460, 78, 12, (18, 24, 34))
    rect(70, band_y, 1460, 2, (46, 56, 74))
    text(92, band_y + 26, "ALSO TODAY", ACCENT, 3)
    ticker = "ENERGY / SHIPPING / RUNOFFS / OPEN MODELS"
    text(360, band_y + 26, ticker, MUTED, 3)

    # footer strip
    rect(70, 800, 1460, 3, (46, 56, 74))
    text(70, 826, "EDITED BY AN AI AGENT / MAKE.FUN / 18 NOV 2026", MUTED, 3)

    raw = b"".join(b"\x00" + bytes(canvas[r * W * 3:(r + 1) * W * 3]) for r in range(H))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    out = "/output/entry.png" if os.path.isdir("/output") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "wb") as f:
        f.write(png)
    print("wrote", out, len(png), "bytes")


if __name__ == "__main__":
    main()

