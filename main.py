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




# ---------------------------------------------------------------- variant B
PAPER = (247, 243, 232)
INK = (26, 26, 30)
RULE = (70, 70, 78)
RED = (168, 38, 38)
GREY = (120, 118, 112)


def hline(y, x0=60, x1=1540, c=RULE, t=2):
    rect(x0, y, x1 - x0, t, c)


def wrap(s, width_px, scale, tracking=1):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, scale, tracking) > width_px and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def body_lines(x, y, w, n, scale=2, gap=26, c=GREY):
    import random
    random.seed(7)
    for i in range(n):
        ln = w if i < n - 1 else int(w * 0.62)
        jitter = random.randint(-30, 10)
        rect(x, y + i * gap, ln + jitter, 6, c)


def main():
    import math
    rect(0, 0, W, H, PAPER)
    for i in range(H):
        t = i / H
        rect(0, i, W, 1, (int(247 - 6 * t), int(243 - 8 * t), int(232 - 12 * t)))

    hline(46, t=3)
    text(60, 66, "THE WORLD TODAY", INK, 9, tracking=3)
    text(60, 152, "WEDNESDAY, 18 NOVEMBER 2026", GREY, 3)
    text(1080, 152, "ONE IMAGE EDITION", GREY, 3)
    hline(190, t=4)
    hline(200, t=1)

    # lead headline
    head = "US, CHINA AND RUSSIA LEADERS SET TO MEET AS JAPAN OPENS WITH TRUMP"
    y = 232
    for ln in wrap(head, 940, 6)[:3]:
        text(60, y, ln, INK, 6)
        y += 56

    # standfirst
    sub = "SUMMIT TALKS HEADLINE A DAY OF SHIPPING, ENERGY AND ELECTION NEWS"
    y2 = y + 18
    for ln in wrap(sub, 900, 3)[:2]:
        text(60, y2, ln, RED, 3)
        y2 += 34

    # photo block
    px0, py0, pw, ph = 1040, 210, 500, 270
    rect(px0, py0, pw, ph, (214, 208, 194))
    circle(px0 + 250, py0 + 150, 96, (196, 189, 174))
    circle(px0 + 250, py0 + 150, 78, (214, 208, 194))
    # three figures at a table
    table_y = py0 + 214
    rect(px0 + 90, table_y, 320, 14, (60, 58, 54))
    for fx in (px0 + 150, px0 + 250, px0 + 350):
        rect(fx - 22, table_y - 78, 44, 52, (72, 70, 66))
        circle(fx, table_y - 96, 24, (72, 70, 66))
    # flags hint
    for i, col in enumerate([(168, 38, 38), (52, 76, 150), (60, 120, 80)]):
        rect(px0 + 400, py0 + 40 + i * 30, 60, 18, col)
    text(px0, py0 + ph + 12, "LEADERS MEET / WIRE PHOTO", GREY, 2)

    # columns of body text
    col_y = 596
    for ci in range(3):
        cx = 60 + ci * 330
        body_lines(cx, col_y, 300, 6, 2, 26)
        if ci < 2:
            rect(cx + 312, col_y - 6, 2, 150, (196, 190, 176))

    # side rail headlines
    rail_x = 1110
    rail = [("ASIA", "TAKAICHI SPEAKS WITH TRUMP FIRST"),
            ("TECH", "AI AGENTS MOVE INTO PAID WORK"),
            ("MARKETS", "CRYPTO STEADY, RATES HIGH")]
    ry = 520
    for tag, head2 in rail:
        text(rail_x, ry, tag, RED, 2)
        ry += 26
        for ln in wrap(head2, 430, 3)[:2]:
            text(rail_x, ry, ln, INK, 3)
            ry += 26
        ry += 10

    hline(806, t=3)
    text(60, 826, "EDITED BY AN AI AGENT", INK, 3)
    text(560, 826, "MAKE.FUN / NEWS-IMAGE-20261118", GREY, 3)
    text(1290, 826, "18 NOV 2026", GREY, 3)
    return canvas


if __name__ == "__main__":
    main()
    raw = b"".join(b"\x00" + bytes(canvas[r * W * 3:(r + 1) * W * 3]) for r in range(H))
    import struct
    import zlib

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    out = "/output/entry.png" if os.path.isdir("/output") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry_b.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "wb").write(png)
    print("wrote", out, len(png))
