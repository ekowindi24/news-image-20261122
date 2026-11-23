#!/usr/bin/env python3
"""Sunday 22 November 2026 in one image.

A 1024x1024 newspaper front page drawn with Python standard library
only. No network, no fonts on disk, no Pillow: the letters come from a
small 5x7 bitmap alphabet written out below, and the PNG bytes are
encoded by hand with zlib. Two runs write the same bytes.
"""
import os
import struct
import zlib

W = 1024
H = 1024
PAPER = (247, 241, 227)
INK = (18, 18, 18)
RED = (178, 34, 34)
TEAL = (0, 110, 110)
BLUE = (24, 68, 140)
GOLD = (184, 134, 11)
GREY = (90, 90, 86)
LIGHT = (232, 224, 205)
WHITE = (255, 255, 255)

# 5x7 bitmap alphabet, all caps. Each glyph is 7 rows of 5 bits.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
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
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        for xx in range(x, x + w):
            self.set(xx, y, c)

    def vline(self, x, y, h, c):
        for yy in range(y, y + h):
            self.set(x, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c):
        for a in range(360):
            import math
            x = cx + int(r * math.cos(a * 3.14159 / 180))
            y = cy + int(r * math.sin(a * 3.14159 / 180))
            self.set(x, y, c)

    def text(self, x, y, s, scale, c, bold=False):
        s = s.upper()
        cx = x
        for ch in s:
            g = GLYPHS.get(ch, GLYPHS[" "])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == "1":
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx, y + row * scale + dy, c)
                                if bold:
                                    self.set(cx + col * scale + dx + 1, y + row * scale + dy, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, cx, y, s, scale, c, bold=False):
        x = cx - self.text_w(s, scale) // 2
        return self.text(x, y, s, scale, c, bold)


def wrap(cv, s, scale, max_w):
    words = s.split()
    lines = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if cv.text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def save_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


REGION_COLOUR = {
    "EUROPE": BLUE,
    "MIDDLE EAST": RED,
    "ASIA": TEAL,
    "AFRICA": GOLD,
    "AMERICAS": (90, 40, 110),
    "OCEANIA": (0, 130, 90),
    "WORLD": INK,
}
FIELD_COLOUR = {
    "WAR": RED,
    "POLITICS": BLUE,
    "CLIMATE": TEAL,
    "ECONOMY": GOLD,
    "TECH": (90, 40, 110),
    "SOCIETY": GREY,
    "SPORT": (0, 130, 90),
}

# (n, region, field, headline, body, data strip, icon, lat, lon)
CARDS = [
    (1, "WORLD", "CLIMATE", "COP31 ENDS WITH NO DEAL",
     "Nearly 200 nations leave Antalya without a climate pact after the EU rejects a text with no fossil-fuel mention. Guterres: deeply disappointing.",
     "200 NATIONS - 2 DAYS OVERTIME", "climate", 36.9, 30.7),
    (2, "AFRICA", "WAR", "SEA DRONES HIT RUSSIAN SHIP IN LIBYA",
     "Libyan officials say six sea drones struck the corvette Merkury at Benghazi; two hit, four were downed. Kyiv and Moscow stay silent on blame.",
     "6 DRONES - 2 HITS - 4 DOWNED", "ship", 32.1, 20.1),
    (3, "MIDDLE EAST", "WAR", "GULF ON EDGE AS TANKERS HIT",
     "Bahrain says Iran struck a civilian plant in Sitra, causing a fire. Iran says it hit US Patriot radars. A tanker incident is probed in the Gulf of Oman.",
     "14 TANKERS READY, IRAN SAYS", "gulf", 26.2, 50.6),
    (4, "MIDDLE EAST", "WAR", "EISENKOT: SETTLER TERROR",
     "Israel's opposition leader condemns settlers who torched 12 vehicles in Ramallah villages overnight.",
     "12 VEHICLES TORCHED", "westbank", 31.9, 35.2),
    (5, "AMERICAS", "POLITICS", "DEMOCRATS WIN 258 SEATS",
     "AP reported on 22 Nov that Democrats secured 258 seats, their largest House majority since 1992.",
     "258 SEATS - MOST SINCE 1992", "us", 38.9, -77.0),
    (6, "AMERICAS", "SPORT", "VERSTAPPEN WINS IN VEGAS",
     "Verstappen beats Norris by 0.639s after 50 laps of lead changes. Ferraris collide; both get 10s penalties.",
     "50 LAPS - WON BY 0.639S", "f1", 36.1, -115.2),
    (7, "EUROPE", "WAR", "186 DRONES IN ONE NIGHT",
     "Ukraine says Russia fired 186 Shahed drones overnight, 72 jet-powered; 161 were downed or jammed.",
     "186 DRONES - 161 DOWNED", "drone", 50.4, 30.5),
    (8, "AMERICAS", "ECONOMY", "WALL ST IN CORRECTION",
     "Reuters reports the S and P 500 is 11.6 percent below its 6 Oct record as the AI sell-off spreads to Japan and Korea.",
     "S AND P -11.6% FROM RECORD", "markets", 40.7, -74.0),
    (9, "WORLD", "TECH", "BEPICOLOMBO REACHES MERCURY",
     "After eight years, the ESA-JAXA craft enters Mercury orbit. A software glitch cuts a burn short; controllers say the spacecraft is safe.",
     "8 YEARS - LAUNCHED 2018", "space", 0.0, 0.0),
    (10, "MIDDLE EAST", "WAR", "AID WORKERS KILLED IN GAZA",
     "Three soup-kitchen workers are killed delivering food in Gaza City; the truce toll is 1,671, monitors say.",
     "TRUCE TOLL 1,671", "gaza", 31.5, 34.5),
    (11, "ASIA", "SOCIETY", "JAVA FACTORY FIRE: 3 DEAD",
     "A blaze at a candy factory in Cikande kills three workers; 36 are still missing as rescuers search the ruins.",
     "3 DEAD - 36 MISSING", "fire", -6.2, 106.2),
    (12, "AFRICA", "SOCIETY", "BOAT CAPSIZES: 24 DEAD",
     "A boat carrying mourners capsizes in Bayelsa, Nigeria, killing 24. The toll later rises to 26, officials say.",
     "24 DEAD - TOLL RISES TO 26", "boat", 4.8, 6.3),
    (13, "AMERICAS", "TECH", "US PROBES NVIDIA CHIPS",
     "US officials probe how Nvidia AI chips reached China despite export curbs, as the NYT reports a Chinese effort to obtain them.",
     "CHIP SMUGGLING PROBE", "chip", 38.9, -77.0),
]

# (n, region, field, one-line brief)
BRIEFS = [
    (14, "EUROPE", "WAR", "Zelensky: 2,700 drones, 1,460 bombs in a week"),
    (15, "EUROPE", "WAR", "Ukraine hits Kerch Bridge railway again"),
    (16, "EUROPE", "WAR", "Dymer: 14 feared trapped after drone hits flats"),
    (17, "EUROPE", "WAR", "Lviv dashcam films Russian strike on building"),
    (18, "EUROPE", "WAR", "Finland tows damaged Sparta II out of its waters"),
    (19, "EUROPE", "POLITICS", "Denmark expels Russian defence attache"),
    (20, "EUROPE", "SOCIETY", "France protests for a sixth weekend"),
    (21, "EUROPE", "SOCIETY", "Belgium warns of flight chaos in strike"),
    (22, "EUROPE", "SOCIETY", "Three French police sentenced over racist assault"),
    (23, "EUROPE", "POLITICS", "Spain heads for 29 Nov vote amid deadlock"),
    (24, "MIDDLE EAST", "POLITICS", "Israel talks: Likud and Yashar still split"),
    (25, "MIDDLE EAST", "POLITICS", "Lebanon's Aoun demands Israeli withdrawal"),
    (26, "MIDDLE EAST", "POLITICS", "Qatar holds talks in Tehran on ending the war"),
    (27, "MIDDLE EAST", "WAR", "Iran unveils underground missile facility"),
    (28, "MIDDLE EAST", "WAR", "Trump warns Iran over alleged dirty-bomb plot"),
    (29, "AMERICAS", "POLITICS", "Trump: contractors must report Congress inquiries"),
    (30, "AMERICAS", "SOCIETY", "ICE detains 2 on Seattle flight; Gilroy protests"),
    (31, "AMERICAS", "SOCIETY", "US Army to blast lead chemicals despite court"),
    (32, "AMERICAS", "TECH", "Amazon in $7.5bn AI deal with Decart"),
    (33, "AMERICAS", "TECH", "FBI investigates a database breach, Reuters says"),
    (34, "AMERICAS", "ECONOMY", "Anthropic IPO sparks row over unusual deal curbs"),
    (35, "ASIA", "ECONOMY", "China eases margin rules to 80% from 30 Nov"),
    (36, "ASIA", "TECH", "China chipmakers CXMT and YMTC gain ground"),
    (37, "ASIA", "POLITICS", "Taiwan warns Canada over China trade ties"),
    (38, "ASIA", "POLITICS", "China-Japan ties sour over Taiwan, minerals"),
    (39, "ASIA", "POLITICS", "India Youth Congress protests at Meta offices"),
    (40, "ASIA", "SOCIETY", "Manipur toxic alcohol: 11 dead, 180 in hospital"),
    (41, "ASIA", "POLITICS", "Philippines: Marcos clarifies Trump trade claim"),
    (42, "AFRICA", "WAR", "Sudan: UN links 1,630 deaths to drone strikes"),
    (43, "AFRICA", "POLITICS", "South Africa ANC in coalition talks"),
    (44, "AFRICA", "SOCIETY", "Mlambo-Ngcuka, ex-deputy president, dies at 71"),
    (45, "AFRICA", "SOCIETY", "DRC Ebola response hit by insecurity, MSF warns"),
    (46, "AFRICA", "POLITICS", "Tinubu rallies in Ibadan, names APC candidate"),
    (47, "AMERICAS", "SOCIETY", "Brazil storm kills 3, injures 162"),
    (48, "AMERICAS", "POLITICS", "Bolsonaro remains in intensive care in Brasilia"),
    (49, "AMERICAS", "POLITICS", "Haiti signs prison deal with El Salvador"),
    (50, "EUROPE", "SPORT", "Liverpool beat Manchester United 4-0"),
    (51, "AMERICAS", "SPORT", "Wembanyama scores 50 in Spurs win"),
    (52, "AMERICAS", "SPORT", "Kansas City Current win the NWSL title"),
]

NUMBERS = [
    ("186", "DRONES ONE NIGHT"),
    ("2,700", "DRONES IN A WEEK"),
    ("258", "HOUSE SEATS"),
    ("-11.6%", "S AND P OFF RECORD"),
    ("6", "SEA DRONES BENGHAZI"),
    ("0.639S", "WIN MARGIN F1"),
]

DATE_CHECK = [
    "NOT ON THIS PAGE - FIRST REPORTED BEFORE 22 NOV:",
    "Shenzhen Trump-Xi-Putin summit (19-20 Nov) - ICJ: Myanmar",
    "guilty of Rohingya genocide (19 Nov) - UK-EU package (20 Nov)",
    "EU-Indonesia trade deal (21 Nov) - El Chapo Isidro held (21 Nov)",
    "Kryvyi Rih missile kills 2 (21 Nov) - GTA 6 day-one sales (21 Nov)",
    "Peru quake M6.7 (21 Nov) - Russian ship ablaze off Finland (21 Nov)",
]


def fill_poly(cv, pts, c):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    for y in range(min(ys), max(ys) + 1):
        for x in range(min(xs), max(xs) + 1):
            inside = False
            j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if (yi > y) != (yj > y):
                    xx = xi + (y - yi) * (xj - xi) / (yj - yi)
                    if x < xx:
                        inside = not inside
                j = i
            if inside:
                cv.set(x, y, c)


def draw_icon(cv, x, y, kind, c):
    # White glyphs drawn in a coloured band, all from primitives.
    if kind == "climate":
        cv.disc(x + 14, y + 12, 8, c)
        cv.rect(x + 2, y + 24, 24, 3, c)
        cv.rect(x + 6, y + 29, 16, 3, c)
    elif kind == "ship":
        cv.rect(x + 2, y + 14, 24, 8, c)
        cv.line(x + 14, y + 14, x + 14, y + 2, c)
        cv.line(x + 14, y + 2, x + 24, y + 12, c)
        cv.rect(x + 2, y + 24, 24, 2, c)
    elif kind == "gulf":
        for k in range(3):
            cv.line(x + 2, y + 6 + k * 8, x + 26, y + 6 + k * 8, c)
            cv.line(x + 6, y + 10 + k * 8, x + 22, y + 10 + k * 8, c)
    elif kind == "westbank":
        cv.rect(x + 4, y + 12, 20, 14, c)
        cv.line(x + 2, y + 12, x + 14, y + 2, c)
        cv.line(x + 26, y + 12, x + 14, y + 2, c)
        cv.rect(x + 11, y + 18, 6, 8, c)
    elif kind == "us":
        for k in range(3):
            cv.rect(x + 2, y + 4 + k * 8, 24, 3, c)
        cv.disc(x + 14, y + 28, 4, c)
    elif kind == "f1":
        for r in range(3):
            for col in range(4):
                if (r + col) % 2 == 0:
                    cv.rect(x + 2 + col * 6, y + 2 + r * 8, 6, 8, c)
    elif kind == "drone":
        cv.disc(x + 14, y + 14, 6, c)
        cv.line(x + 2, y + 2, x + 26, y + 26, c)
        cv.line(x + 26, y + 2, x + 2, y + 26, c)
    elif kind == "markets":
        cv.rect(x + 2, y + 18, 5, 10, c)
        cv.rect(x + 11, y + 10, 5, 18, c)
        cv.rect(x + 20, y + 4, 5, 24, c)
    elif kind == "space":
        cv.disc(x + 14, y + 14, 8, c)
        cv.line(x + 2, y + 20, x + 26, y + 8, c)
        cv.disc(x + 24, y + 4, 2, c)
    elif kind == "gaza":
        cv.rect(x + 4, y + 6, 20, 20, c)
        cv.rect(x + 12, y + 10, 4, 12, INK)
        cv.rect(x + 8, y + 14, 12, 4, INK)
    elif kind == "fire":
        cv.line(x + 14, y + 2, x + 24, y + 20, c)
        cv.line(x + 24, y + 20, x + 4, y + 20, c)
        cv.line(x + 4, y + 20, x + 14, y + 2, c)
        cv.disc(x + 14, y + 20, 4, c)
    elif kind == "boat":
        cv.rect(x + 2, y + 12, 24, 7, c)
        cv.line(x + 14, y + 12, x + 14, y + 2, c)
        cv.rect(x + 2, y + 22, 24, 2, c)
    elif kind == "chip":
        cv.rect(x + 6, y + 6, 16, 16, c)
        cv.rect(x + 11, y + 11, 6, 6, INK)
        for k in range(3):
            cv.rect(x + 2 + k * 8, y + 2, 3, 4, c)
            cv.rect(x + 2 + k * 8, y + 22, 3, 4, c)


def draw_card(cv, x, y, w, h, card, big):
    n, region, field, head, body, data, icon, _lat, _lon = card
    col = REGION_COLOUR[region]
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 2, col)
    cv.rect(x, y, 2, h, col)
    cv.rect(x + w - 2, y, 2, h, col)
    cv.rect(x, y + h - 2, w, 2, col)
    band = 36 if big else 30
    cv.rect(x + 2, y + 2, w - 4, band, col)
    cv.text(x + 8, y + 6, str(n), 3 if big else 2, WHITE, bold=True)
    cv.text(x + w - 44, y + 8, field, 1, WHITE, bold=True)
    draw_icon(cv, x + 52, y + 4, icon, WHITE)
    ty = y + band + 6
    cv.text(x + 8, ty, region, 1, RED, bold=True)
    ty += 12
    hs = 2
    lines = wrap(cv, head, hs, w - 16)
    for ln in lines[:2]:
        cv.text(x + 8, ty, ln, hs, INK, bold=True)
        ty += 15
    ty += 2
    blines = wrap(cv, body, 1, w - 16)
    max_body = 5 if big else 4
    for ln in blines[:max_body]:
        cv.text(x + 8, ty, ln, 1, INK)
        ty += 9
    cv.rect(x + 8, y + h - 18, w - 16, 1, LIGHT)
    cv.text(x + 8, y + h - 15, data, 1, GREY, bold=True)


def main():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, H, PAPER)
    cv.rect(6, 6, W - 12, H - 12, INK)
    cv.rect(8, 8, W - 16, H - 16, PAPER)
    # Masthead
    cv.text_center(512, 16, "THE WORLD IN ONE DAY", 4, INK, bold=True)
    cv.text_center(512, 52, "SUNDAY 22 NOVEMBER 2026", 3, RED, bold=True)
    cv.text_center(512, 80, "52 STORIES - 6 CONTINENTS - EVERY STORY SOURCED", 1, INK, bold=True)
    cv.hline(16, 98, 992, INK)
    # Counts
    all_stories = [(c[1], c[2]) for c in CARDS] + [(b[1], b[2]) for b in BRIEFS]
    regions = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]
    fields = ["WAR", "POLITICS", "CLIMATE", "ECONOMY", "TECH", "SOCIETY", "SPORT"]
    rc = {r: sum(1 for a, _f in all_stories if a == r) for r in regions}
    fc = {f: sum(1 for _a, b in all_stories if b == f) for f in fields}
    # Region ribbon
    y = 102
    cv.rect(16, y, 992, 20, INK)
    parts = []
    for r in regions:
        if rc[r]:
            parts.append("%s %d" % (r, rc[r]))
    cv.text(24, y + 3, "  |  ".join(parts), 1, WHITE, bold=True)
    # Field ribbon
    y = 124
    cv.rect(16, y, 992, 20, WHITE)
    cv.rect(16, y, 992, 1, INK)
    cv.rect(16, y + 19, 992, 1, INK)
    parts = []
    for f in fields:
        if fc[f]:
            parts.append("%s %d" % (f, fc[f]))
    cv.text(24, y + 3, "BY FIELD:  " + "  |  ".join(parts), 1, INK, bold=True)
    # Day in numbers
    y = 148
    cv.text(16, y, "THE DAY IN NUMBERS", 1, RED, bold=True)
    x = 16
    for num, label in NUMBERS:
        cv.text(x, y + 12, num, 2, INK, bold=True)
        cv.text(x, y + 26, label, 1, GREY)
        x += 168
    cv.hline(16, 182, 992, INK)
    # Top 3 cards
    for i, card in enumerate(CARDS[:3]):
        draw_card(cv, 16 + i * 333, 188, 325, 168, card, True)
    # Rows of 5
    for row, cards in enumerate((CARDS[3:8], CARDS[8:13])):
        for i, card in enumerate(cards):
            draw_card(cv, 16 + i * 200, 362 + row * 152, 192, 146, card, False)
    # Briefs
    cv.text(16, 668, "THE REST OF THE DAY - 39 MORE STORIES", 2, INK, bold=True)
    cv.hline(16, 686, 992, INK)
    for idx, (n, region, _field, txt) in enumerate(BRIEFS):
        col = idx % 3
        row = idx // 3
        bx = 16 + col * 333
        by = 692 + row * 14
        cv.text(bx, by, str(n) + ".", 1, RED, bold=True)
        cv.text(bx + 24, by, txt[:49], 1, INK)
    cv.hline(16, 876, 992, INK)
    # Map
    mx, my, mw, mh = 16, 882, 484, 130
    cv.rect(mx, my, mw, mh, LIGHT)
    cv.text(mx + 8, my + 4, "WHERE IT HAPPENED", 1, INK, bold=True)
    continents = [
        [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60), (-80, 45), (-95, 30), (-105, 20), (-120, 25), (-140, 40), (-160, 55)],
        [(-80, 10), (-60, 5), (-35, -5), (-40, -20), (-55, -35), (-70, -50), (-75, -30), (-80, -10)],
        [(-10, 36), (0, 44), (10, 45), (20, 55), (30, 60), (25, 70), (10, 70), (-5, 60), (-10, 50)],
        [(-17, 15), (-10, 35), (10, 37), (30, 31), (43, 12), (51, 10), (40, -5), (35, -20), (20, -35), (12, -18), (8, 4), (-8, 5)],
        [(30, 70), (60, 70), (90, 75), (120, 73), (160, 70), (180, 65), (160, 55), (140, 40), (120, 30), (100, 10), (90, 20), (70, 10), (50, 25), (40, 35)],
        [(113, -22), (130, -12), (142, -11), (150, -22), (150, -37), (135, -38), (120, -35), (113, -30)],
    ]
    for cont in continents:
        pts = []
        for lon, lat in cont:
            px = mx + int((lon + 180) / 360 * mw)
            py = my + 18 + int((90 - lat) / 180 * (mh - 18))
            pts.append((px, py))
        fill_poly(cv, pts, (200, 190, 160))
    for card in CARDS:
        n, _r, _f, _h, _b, _d, _ic, lat, lon = card
        if lat == 0.0 and lon == 0.0:
            continue
        px = mx + int((lon + 180) / 360 * mw)
        py = my + 18 + int((90 - lat) / 180 * (mh - 18))
        cv.disc(px, py, 8, RED)
        cv.disc(px, py, 8, RED)
        label = str(n)
        cv.text(px - 3 if len(label) == 1 else px - 6, py - 3, label, 1, WHITE, bold=True)
    # Date check + sources
    dx = 508
    cv.rect(dx, 882, 500, 130, WHITE)
    cv.rect(dx, 882, 500, 2, RED)
    ty = 888
    for ln in DATE_CHECK:
        cv.text(dx + 8, ty, ln, 1, INK, bold=(ty == 888))
        ty += 13
    ty += 4
    cv.text(dx + 8, ty, "SOURCES: REUTERS, AP, AFP, BBC, AL JAZEERA,", 1, GREY)
    ty += 13
    cv.text(dx + 8, ty, "ESA, UKMTO, NYT, GUARDIAN. ALL 52 STORIES", 1, GREY)
    ty += 13
    cv.text(dx + 8, ty, "HAPPENED OR FIRST REPORTED 22 NOV 2026.", 1, GREY, bold=True)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError:
        outdir = "."
    save_png(cv, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
