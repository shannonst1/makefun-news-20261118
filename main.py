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




# ---------------------------------------------------------------- variant C
BG2 = (8, 12, 22)
LAND = (34, 44, 60)
LAND2 = (46, 58, 78)
GLOW = (255, 196, 64)
BLUE = (92, 160, 255)
GREEN = (110, 220, 170)
PINK = (240, 130, 190)


def blob(cx, cy, rx, ry, c):
    for dy in range(-ry, ry + 1):
        span = int(rx * (1 - (dy * dy) / float(ry * ry)) ** 0.5)
        rect(cx - span, cy + dy, span * 2 + 1, 1, c)


def ring(cx, cy, r, c, t=2):
    steps = max(24, r * 3)
    for i in range(steps):
        a = 2 * 3.1415926 * i / steps
        import math
        x = int(cx + r * math.cos(a))
        y = int(cy + r * math.sin(a))
        rect(x, y, t, t, c)


def main():
    import math

    rect(0, 0, W, H, BG2)
    for i in range(H):
        t = i / H
        rect(0, i, W, 1, (int(8 + 6 * t), int(12 + 8 * t), int(22 + 12 * t)))

    # graticule
    for gx in range(80, W, 120):
        rect(gx, 0, 1, H, (16, 22, 34))
    for gy in range(60, H, 120):
        rect(0, gy, W, 1, (16, 22, 34))

    # continents (rough)
    blob(330, 300, 120, 95, LAND)     # north america
    blob(420, 470, 70, 110, LAND)     # south america
    blob(760, 330, 85, 80, LAND)      # europe
    blob(830, 520, 105, 130, LAND)    # africa
    blob(1080, 300, 190, 110, LAND)   # asia
    blob(1230, 520, 90, 55, LAND)     # oceania
    blob(360, 250, 60, 45, LAND2)
    blob(1120, 260, 120, 60, LAND2)

    text(60, 48, "THE WORLD ON 18 NOVEMBER 2026", (238, 242, 248), 5)
    rect(60, 110, 700, 2, (60, 74, 96))

    spots = [
        (330, 300, GLOW, "WASHINGTON", "SUMMIT SET: US, CHINA AND RUSSIA LEADERS TO MEET"),
        (1130, 300, BLUE, "TOKYO", "JAPAN PM TAKAICHI OPENS WITH TRUMP FIRST"),
        (760, 330, GREEN, "BRUSSELS", "AI AGENTS MOVE FROM DEMOS INTO PAID WORK"),
        (830, 520, PINK, "LAGOS", "CRYPTO STEADY AS RATES STAY HIGH"),
    ]
    for i, (cx, cy, col, city, head) in enumerate(spots, 1):
        ring(cx, cy, 36, (col[0] // 2, col[1] // 2, col[2] // 2), 2)
        ring(cx, cy, 22, col, 2)
        circle(cx, cy, 9, col)
        circle(cx, cy, 3, (8, 12, 22))
        text(cx - 7, cy - 8, str(i), (8, 12, 22), 2)

    # legend: two columns, two rows
    for i, (cx, cy, col, city, head) in enumerate(spots):
        lx = 60 + (i % 2) * 760
        ly = 556 + (i // 2) * 116
        rect(lx, ly - 4, 6, 34, col)
        text(lx + 24, ly, str(i + 1), col, 3)
        text(lx + 66, ly, city, col, 3)
        text(lx + 66, ly + 36, head, (226, 232, 242), 2)

    # bottom legend
    rect(60, 730, 1480, 2, (60, 74, 96))
    text(60, 758, "FOUR STORIES / ONE DAY / ONE IMAGE", (150, 164, 184), 3)
    text(1150, 758, "MAKE.FUN 18 NOV 2026", (150, 164, 184), 3)


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
    out = "/output/entry.png" if os.path.isdir("/output") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry_c.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "wb").write(png)
    print("wrote", out, len(png))
