"""news-image-20261122 v1: one front page summing up Sunday 22 November 2026.

Morning v1, researched on 22 Nov 2026 up to ~08:30 WIB from live wires
(Reuters, AP, AAP, BBC, Al Jazeera, AFP roundups). It carries the news
cycle of Sunday 22 November as Sunday's papers lead with it: the COP31
final deal package unveiled overnight in Antalya, Iran massing tankers
off Kharg to test the US blockade, Zelensky on the four-nation talks,
fresh Israeli strikes on south Lebanon, Trump's order gagging federal
contractors, the Las Vegas Grand Prix under the lights, the EU budget
tech-levy fight, the Nigeria boat sinking, Denmark expelling a Russian
attache, a Chinese bomber turning back from Manila, the UN report on
women, the Basra plant fire and the AI war of words. Every figure comes
from that research; nothing is invented. Stories first reported on 21 Nov
or earlier (Iran's Bahrain strikes, Kryvyi Rih, the EU-Indonesia deal,
El Chapo Isidro, the Peru quake, the Russian ship ablaze off Finland,
GTA 6 day-one sales, the Kyiv barrage) are NOT on the page; they are
named in DATE CHECK. A full-day v2 tomorrow morning can tighten the
dating further and carry the COP31 vote and the Vegas result.

Draws a 1024x1024 PNG with Python stdlib only, no network, fully
deterministic: the same bytes on every run.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 241, 222)
INK = (18, 18, 18)
RED = (176, 32, 28)
TEAL = (0, 104, 104)
BLUE = (28, 76, 158)
GOLD = (176, 124, 0)
GREEN = (38, 112, 58)
PURPLE = (104, 64, 140)
GREY = (96, 96, 92)
LIGHT = (236, 229, 206)
SKY = (178, 205, 224)
LAND = (206, 198, 168)
SEA = (214, 228, 236)

REGION_COLOR = {
    "EUROPE": BLUE, "MIDDLE EAST": RED, "ASIA": TEAL, "AFRICA": GOLD,
    "AMERICAS": GREEN, "OCEANIA": PURPLE, "WORLD": GREY,
}

# 5x7 bitmap font, one 35-char row-major string per glyph ('#' = ink).
FONT = {
    "A": "01110100011000111111100011000110001",
    "B": "11110100011000111110100011000111110",
    "C": "01110100011000010000100001000101110",
    "D": "11110100011000110001100011000111110",
    "E": "11111100001000011110100001000011111",
    "F": "11111100001000011110100001000010000",
    "G": "01110100011000010111100011000101111",
    "H": "10001100011000111111100011000110001",
    "I": "01110001000010000100001000010001110",
    "J": "00111000100001000010000101001001100",
    "K": "10001100101010011000101001001010001",
    "L": "10000100001000010000100001000011111",
    "M": "10001110111010110101100011000110001",
    "N": "10001110011010110011100011000110001",
    "O": "01110100011000110001100011000101110",
    "P": "11110100011000111110100001000010000",
    "Q": "01110100011000110001101011001001101",
    "R": "11110100011000111110101001001010001",
    "S": "01111100001000001110000010000111110",
    "T": "11111001000010000100001000010000100",
    "U": "10001100011000110001100011000101110",
    "V": "10001100011000110001100010101000100",
    "W": "10001100011000110101101011101110001",
    "X": "10001100010101000100010101000110001",
    "Y": "10001100010101000100001000010000100",
    "Z": "11111000010001000100010001000011111",
    "0": "01110100011001110101110011000101110",
    "1": "00100011000010000100001000010001110",
    "2": "01110100010000100110010001000011111",
    "3": "11110000010000101110000010000111110",
    "4": "00010001100101010010111110001000010",
    "5": "11111100001111000001000011000101110",
    "6": "01110100001000011110100011000101110",
    "7": "11111000010001000100010001000010000",
    "8": "01110100011000101110100011000101110",
    "9": "01110100011000101111000010000101110",
    " ": "...................................",
    ".": ".........................0110001100",
    ",": "....................011000010001000",
    ":": ".....0110001100.....0110001100.....",
    ";": ".....0110001100.....011000100000100",
    "-": "...............11111...............",
    "/": "00001000100010000100010001000010000",
    "%": "11001110100001000100010000101110011",
    "$": "00100011111010001110001011111000100",
    "(": "00010001000100001000010000100000100",
    ")": "01000001000001000010000100010001000",
    "'": "001000010001000....................",
    "!": "00100001000010000100001000000000100",
    "?": "01110100010000100110001000000000100",
    "+": ".....0010000100111110010000100.....",
    "&": "01100100101010001000101011001001101",
    "=": "..........11111.....11111..........",
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def box(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self._set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self._set(xx, yy, c)

    def ring(self, cx, cy, r, c):
        for a in range(360):
            import math
            self._set(cx + int(r * math.cos(math.radians(a))),
                      cy + int(r * math.sin(math.radians(a))), c)

    def glyph(self, ch, x, y, c, s):
        g = FONT.get(ch, FONT[" "])
        g = (g + "." * 35)[:35]
        for row in range(7):
            for col in range(5):
                if g[row * 5 + col] == "1":
                    self.fill(x + col * s, y + row * s, s, s, c)

    def text(self, x, y, s, c, scale=1):
        cx = x
        for ch in s.upper():
            self.glyph(ch, cx, y, c, scale)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale - scale

    def text_center(self, cx, y, s, c, scale=1):
        self.text(cx - self.text_w(s, scale) // 2, y, s, c, scale)

    def wrap(self, s, max_chars):
        lines, cur = [], ""
        for w in s.split():
            if cur and len(cur) + 1 + len(w) > max_chars:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        return lines


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


# ---- story data: 42 stories, Sunday 22 November 2026 ----
# cards: num, region, field, kicker, headline, body, data strip, art, lat, lon
CARDS = [
    (1, "EUROPE", "CLIMATE", "ANTALYA - COP31", "COP31 DEAL AT DAWN",
     "Package unveiled overnight; Australia and Turkey hope all agree; vote due 06:00 GMT.",
     "VOTE DUE 06:00 GMT", "climate", 36.9, 30.7),
    (2, "MIDDLE EAST", "WAR", "GULF - KHARG ISLAND", "IRAN MASSES TANKERS",
     "14 tankers stage off Kharg to test the US blockade; Bahrain counts Saturday damage.",
     "14 TANKERS OFF KHARG", "sea", 26.5, 56.0),
    (3, "EUROPE", "WAR", "KYIV - UKRAINE", "ZELENSKY: TALKS MUST DELIVER",
     "Four-nation peace talks must yield results, Zelensky says; US presses January deal.",
     "4-NATION TALKS DUE", "summit", 50.45, 30.52),
    (4, "MIDDLE EAST", "WAR", "GAZA - LEBANON", "ISRAEL STRIKES SOUTH LEBANON",
     "Fresh strikes hit south Lebanon; 6 hurt in Gaza; floods swamp children.",
     "6 WOUNDED IN GAZA", "strike", 33.3, 35.5),
    (5, "AMERICAS", "POLITICS", "WASHINGTON", "TRUMP GAGS CONTRACTORS",
     "Federal contractors must clear Congress queries with the White House or lose deals.",
     "CLEAR IT OR LOSE IT", "court", 38.9, -77.04),
    (6, "AMERICAS", "SPORT", "LAS VEGAS - F1", "VERSTAPPEN ON POLE IN VEGAS",
     "Lights out 04:00 GMT; champion Antonelli starts P6 after a 5-place grid penalty.",
     "RACE 04:00 GMT", "flag", 36.17, -115.14),
    (7, "EUROPE", "POLITICS", "BRUSSELS - EU", "EU BUDGET: TECH LEVY PLAN",
     "Costa plans 3 pct levy on big tech in a 204bn-euro budget; France says no.",
     "3 PCT LEVY - 204BN CUT", "handshake", 50.85, 4.35),
    (8, "AFRICA", "DISASTER", "NIGERIA", "BOAT CAPSIZES: 24 DEAD",
     "Boat carrying mourners to a burial capsizes in the south; 24 killed, others missing.",
     "24 DEAD EN ROUTE", "sea", 6.5, 3.4),
    (9, "EUROPE", "POLITICS", "COPENHAGEN", "DENMARK EXPELS RUSSIAN ATTACHE",
     "Envoy expelled after a foiled plot targeting a Ukrainian artist, officials say.",
     "PLOT FOILED - ENVOY OUT", "court", 55.68, 12.57),
    (10, "ASIA", "WAR", "MANILA - SOUTH CHINA SEA", "CHINA JET NEARS MANILA",
     "Missile-carrying bomber flies toward the Philippine capital, turns back 170 km out.",
     "TURNS BACK 170 KM OUT", "plane", 14.6, 120.98),
    (11, "WORLD", "SOCIETY", "WORLDWIDE - UN", "1 IN 4 WOMEN CANNOT SAY NO",
     "UN: one in four partnered women cannot refuse sex; one in three in Arab states.",
     "1 IN 4 - 1 IN 3 ARAB", "report", None, None),
    (12, "MIDDLE EAST", "DISASTER", "BASRA - IRAQ", "BASRA POWER PLANT FIRE",
     "Blaze at an electricity plant kills 4 and injures 35; crews battle the fire for hours.",
     "4 DEAD - 35 INJURED", "tower", 30.5, 47.8),
    (13, "AMERICAS", "TECH", "WASHINGTON - AI", "AI WAR OF WORDS",
     "Trump eyes levy on firms building data centres abroad; Congress wants Chinese AI out.",
     "LEVY EYED - BAN PUSHED", "chip", 38.9, -77.04),
]

# briefs: num, region, field, one-line text
BRIEFS = [
    (14, "AMERICAS", "POLITICS", "Bessent: no new Nvidia curbs for China"),
    (15, "EUROPE", "POLITICS", "EU floats online tax; France, Germany split"),
    (16, "ASIA", "POLITICS", "Taiwan takes up drone warfare as Trump nears Xi"),
    (17, "WORLD", "POLITICS", "States eye killer-robot rules by 2028"),
    (18, "MIDDLE EAST", "WAR", "Houthi missiles at Riyadh stopped, Saudis say"),
    (19, "AMERICAS", "POLITICS", "Jeffries vows early push to end Iran war"),
    (20, "MIDDLE EAST", "POLITICS", "Trump vows enduring Iran deal, no nukes"),
    (21, "ASIA", "POLITICS", "US-China military talks end in Shanghai"),
    (22, "AMERICAS", "POLITICS", "Canada PM dodges US curbs report"),
    (23, "AFRICA", "ECONOMY", "Senegal farmers on climate front line"),
    (24, "MIDDLE EAST", "WAR", "UN: Hodeidah strikes risk aid lifeline"),
    (25, "MIDDLE EAST", "POLITICS", "Iraq retakes Hezbollah stronghold"),
    (26, "AMERICAS", "POLITICS", "Halifax chief doubts US leadership"),
    (27, "AMERICAS", "TECH", "Senator: AI chip sales risk security"),
    (28, "EUROPE", "WAR", "Finland restores Gulf flight curbs"),
    (29, "EUROPE", "POLITICS", "SBU lobbies MPs over transparency bill"),
    (30, "AMERICAS", "JUSTICE", "Court blocks Iowa lead-drums blast"),
    (31, "EUROPE", "JUSTICE", "Russia brands Insider reporter agent"),
    (32, "MIDDLE EAST", "POLITICS", "US backs strong, united Kurdistan"),
    (33, "MIDDLE EAST", "ECONOMY", "Pezeshkian: Iran fights silent war"),
    (34, "MIDDLE EAST", "POLITICS", "Fidan, Kalin meet Libya PM in Istanbul"),
    (35, "AMERICAS", "DISASTER", "Couple shot dead outside Canada Walmart"),
    (36, "MIDDLE EAST", "WAR", "Saudi dual alerts; Riyadh danger eases"),
    (37, "EUROPE", "POLITICS", "France, US draft post-UNIFIL text"),
    (38, "WORLD", "POLITICS", "US open to Latin American UN chief"),
    (39, "ASIA", "POLITICS", "Pakistan: death for blasphemy posts"),
    (40, "EUROPE", "JUSTICE", "Italy ex-police chief dies in probe"),
    (41, "ASIA", "POLITICS", "Dhaka blames Awami League for violence"),
    (42, "EUROPE", "WAR", "Fresh Russian strikes hit Kyiv overnight"),
]

NUMBERS = [
    ("14 TANKERS", "IRAN OFF KHARG"),
    ("24 DEAD", "NIGERIA BOAT"),
    ("3 PCT", "EU BIG-TECH LEVY"),
    ("1 IN 4", "WOMEN: NO REFUSAL"),
    ("06:00 GMT", "COP31 VOTE DUE"),
    ("170 KM", "CHINA JET TURNS"),
]

DATE_CHECK = ("DATE CHECK - FIRST REPORTED 21 NOV OR EARLIER, LEFT OUT: "
              "IRAN STRIKES ON US BASES IN BAHRAIN (21 NOV) - KRYVYI RIH "
              "DOUBLE-TAP (21 NOV) - EU-INDONESIA TRADE DEAL (21 NOV) - "
              "EL CHAPO ISIDRO CAPTURED (21 NOV) - PERU QUAKE 6.7 (21 NOV) - "
              "RUSSIAN SHIP ABLAZE OFF FINLAND (21 NOV) - GTA 6 DAY-ONE "
              "3.8BN USD (20 NOV) - KYIV BARRAGE 110 MISSILES (20 NOV).")


def tally(items, idx):
    out = {}
    for it in items:
        k = it[idx]
        out[k] = out.get(k, 0) + 1
    return out


ALL = [(c[0], c[1], c[2]) for c in CARDS] + [(b[0], b[1], b[2]) for b in BRIEFS]
REGION_COUNTS = tally(ALL, 1)
FIELD_COUNTS = tally(ALL, 2)


# ---- flat editorial art for the illustrated cards ----
def art_strike(cv, x, y, w, h):
    cv.fill(x, y, w, h, (32, 32, 44))
    cv.fill(x, y + h - 18, w, 18, INK)
    for bx, bw, bh in ((4, 22, 26), (32, 16, 38), (54, 26, 22)):
        cv.fill(x + bx, y + h - 18 - bh, bw, bh, (70, 70, 84))
    cv.circle(x + w - 26, y + 22, 12, (240, 160, 40))
    cv.circle(x + w - 26, y + 22, 6, (255, 220, 90))
    cv.line(x + 8, y + h - 20, x + w - 30, y + 26, (240, 160, 40))
    cv.line(x + 14, y + h - 20, x + w - 22, y + 34, (240, 160, 40))


def art_court(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + 6, y + 8, w - 12, 8, INK)
    for cx in (14, w // 2 - 4, w - 22):
        cv.fill(x + cx, y + 18, 8, h - 26, INK)
    cv.fill(x + 4, y + h - 10, w - 8, 6, INK)
    cv.circle(x + w // 2, y + h // 2 - 4, 7, RED)
    cv.line(x + w // 2 - 16, y + h // 2 - 4, x + w // 2 + 16, y + h // 2 - 4, RED)


def art_summit(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + h - 12, w, 12, (120, 90, 60))
    for i, col in enumerate((RED, (220, 220, 220), BLUE)):
        px = x + 12 + i * (w // 3)
        cv.vline(px, y + 8, h - 24, INK, 2)
        cv.fill(px + 2, y + 8, 26, 14, col)
    cv.fill(x + w // 2 - 18, y + h - 26, 36, 14, INK)


def art_tower(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x + w // 2 - 12, y + 6, 24, h - 6, (60, 60, 78))
    for wy in range(y + 12, y + h - 8, 9):
        for wx in (x + w // 2 - 8, x + w // 2 + 2):
            cv.fill(wx, wy, 5, 4, (255, 220, 90))
    cv.circle(x + 16, y + 14, 8, (240, 160, 40))
    cv.circle(x + 16, y + 14, 4, (255, 220, 90))
    cv.line(x + 16, y + 14, x + w // 2 - 12, y + 20, RED)


def art_climate(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.circle(x + w - 22, y + 18, 11, (240, 190, 40))
    cv.fill(x, y + h - 16, w, 16, GREEN)
    cv.circle(x + w // 2, y + h - 22, 12, TEAL)
    cv.line(x + w // 2, y + h - 22, x + w // 2 + 14, y + h - 34, TEAL)
    cv.line(x + 10, y + 12, x + 26, y + 12, RED)
    cv.line(x + 18, y + 4, x + 18, y + 20, RED)


def art_chip(cv, x, y, w, h):
    cv.fill(x, y, w, h, INK)
    cv.fill(x + w // 2 - 16, y + h // 2 - 16, 32, 32, TEAL)
    cv.fill(x + w // 2 - 8, y + h // 2 - 8, 16, 16, PAPER)
    for px in range(x + 8, x + w - 8, 12):
        cv.vline(px, y + 2, 8, GOLD, 2)
        cv.vline(px, y + h - 10, 8, GOLD, 2)
    for py in range(y + 8, y + h - 8, 12):
        cv.hline(x + 2, py, 8, GOLD, 2)
        cv.hline(x + w - 10, py, 8, GOLD, 2)


def art_handshake(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.circle(x + w // 2 - 16, y + h // 2, 16, BLUE)
    cv.circle(x + w // 2 + 16, y + h // 2, 16, RED)
    cv.fill(x + w // 2 - 10, y + h // 2 - 5, 20, 10, PAPER)
    for sx in range(x + 8, x + w - 8, 14):
        cv.circle(sx, y + 8, 2, GOLD)


def art_sea(cv, x, y, w, h):
    cv.fill(x, y, w, h, SEA)
    cv.fill(x + w // 2 - 16, y + 8, 32, 12, INK)
    cv.fill(x + w // 2 - 4, y + 20, 8, 18, INK)
    for wy in (y + h - 22, y + h - 14, y + h - 6):
        for wx in range(x + 4, x + w - 4, 12):
            cv.line(wx, wy, wx + 6, wy - 3, BLUE)
            cv.line(wx + 6, wy - 3, wx + 12, wy, BLUE)


def art_flag(cv, x, y, w, h):
    cv.fill(x, y, w, h, (32, 32, 44))
    cv.fill(x, y + h - 14, w, 14, (60, 60, 70))
    for dx in range(x + 6, x + w - 6, 8):
        cv.fill(dx, y + h - 10, 4, 2, (240, 220, 40))
    cv.vline(x + 12, y + 6, h - 20, PAPER, 2)
    fx, fy, cs = x + 14, y + 8, 7
    for r in range(3):
        for c in range(5):
            col = INK if (r + c) % 2 == 0 else PAPER
            cv.fill(fx + c * cs, fy + r * cs, cs, cs, col)
    cv.box(fx, fy, 5 * cs, 3 * cs, INK)
    cv.circle(x + w - 22, y + 16, 8, (240, 160, 40))
    cv.line(x + w - 46, y + h - 16, x + w - 30, y + h - 30, RED)
    cv.line(x + w - 30, y + h - 30, x + w - 14, y + h - 16, RED)


def art_plane(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.circle(x + w - 20, y + 14, 9, (240, 190, 40))
    cx, cy = x + w // 2, y + h // 2
    cv.fill(cx - 34, cy - 4, 68, 8, INK)
    cv.line(cx - 34, cy, cx - 46, cy - 8, INK)
    cv.line(cx - 34, cy, cx - 46, cy + 8, INK)
    cv.fill(cx + 6, cy - 16, 10, 12, INK)
    cv.fill(cx - 8, cy + 4, 12, 14, INK)
    cv.circle(cx + 34, cy, 4, INK)
    cv.line(cx - 46, cy + 2, x + 6, cy + 10, PAPER)
    cv.line(cx - 46, cy + 6, x + 14, cy + 14, PAPER)
    for sx in (10, w - 16):
        cv.circle(x + sx, y + h - 10, 2, PAPER)


def art_report(cv, x, y, w, h):
    cv.fill(x, y, w, h, LIGHT)
    cv.fill(x + w // 2 - 26, y + 6, 52, h - 12, PAPER)
    cv.box(x + w // 2 - 26, y + 6, 52, h - 12, INK)
    for i, lw in enumerate((38, 38, 30, 38)):
        cv.hline(x + w // 2 - 19, y + 16 + i * 9, lw, INK, 1)
    cv.circle(x + w // 2 + 26, y + h - 16, 8, RED)
    cv.circle(x + w // 2 + 26, y + h - 16, 4, PAPER)
    cv.fill(x + 8, y + 8, 10, 10, TEAL)
    cv.fill(x + w - 18, y + 8, 10, 10, GOLD)


ART = {
    "strike": art_strike, "court": art_court, "summit": art_summit,
    "tower": art_tower, "climate": art_climate, "chip": art_chip,
    "handshake": art_handshake, "sea": art_sea, "flag": art_flag,
    "plane": art_plane, "report": art_report,
}


def draw_card(cv, x, y, w, h, card):
    num, region, field, kicker, headline, body, strip, art, lat, lon = card
    accent = REGION_COLOR[region]
    cv.box(x, y, w, h, INK)
    cv.fill(x + 1, y + 1, w - 2, 15, accent)
    kick = ("%d. %s" % (num, kicker))[: (w - 8) // 6]
    cv.text(x + 5, y + 4, kick, PAPER, 1)
    lines = cv.wrap(headline, (w - 10) // 12)[:2]
    for i, ln in enumerate(lines):
        cv.text(x + 5, y + 22 + i * 15, ln, INK, 2)
    art_h = 58 if h > 170 else 46
    ay = y + 56
    cv.box(x + 4, ay, w - 8, art_h, INK)
    ART[art](cv, x + 5, ay + 1, w - 10, art_h - 2)
    blines = cv.wrap(body, (w - 10) // 6)[:3]
    for i, ln in enumerate(blines):
        cv.text(x + 5, ay + art_h + 6 + i * 9, ln, INK, 1)
    cv.fill(x + 1, y + h - 16, w - 2, 15, LIGHT)
    cv.hline(x + 1, y + h - 16, w - 2, INK, 1)
    cv.text_center(x + w // 2, y + h - 13, strip[: (w - 8) // 6], RED, 1)


LAND_RECTS = [
    (-168, -55, 15, 72), (-105, -78, 7, 18), (-80, -35, -55, 12),
    (-11, 32, 36, 60), (-5, 30, 58, 71), (-18, 52, -35, 32),
    (32, 60, 12, 42), (60, 180, 45, 75), (65, 100, 7, 35),
    (95, 141, -10, 28), (113, 154, -39, -11),
]


def draw_map(cv, x, y, w, h):
    cv.box(x, y, w, h, INK)
    cv.text(x + 6, y + 5, "WHERE IT HAPPENED - 12 EARTH PINS", INK, 1)
    mx, my, mw, mh = x + 4, y + 18, w - 8, h - 34
    cv.fill(mx, my, mw, mh, SEA)
    for lon0, lon1, lat0, lat1 in LAND_RECTS:
        px = mx + int((lon0 + 180) / 360 * mw)
        py = my + int((90 - lat1) / 180 * mh)
        pw = int((lon1 - lon0) / 360 * mw)
        ph = int((lat1 - lat0) / 180 * mh)
        cv.fill(px, py, pw, ph, LAND)
    for lon in range(-120, 181, 60):
        gx = mx + int((lon + 180) / 360 * mw)
        cv.vline(gx, my, mh, (190, 205, 215), 1)
    for lat in (-30, 0, 30, 60):
        gy = my + int((90 - lat) / 180 * mh)
        cv.hline(mx, gy, mw, (190, 205, 215), 1)
    placed = []
    for card in CARDS:
        num, lat, lon = card[0], card[8], card[9]
        if lat is None:
            continue
        px = mx + int((lon + 180) / 360 * mw)
        py = my + int((90 - lat) / 180 * mh)
        # nudge pins that would sit on top of an earlier pin
        while any(abs(px - qx) < 14 and abs(py - qy) < 14 for qx, qy in placed):
            px += 14
            if px > mx + mw - 10:
                px -= 28
                py += 14
        placed.append((px, py))
        cv.circle(px, py, 7, RED)
        cv.circle(px, py, 7, PAPER)
        cv.circle(px, py, 6, RED)
        cv.text_center(px, py - 3, str(num), PAPER, 1)


def ribbon(cv, y, segments, colors):
    total = 0
    for label, count in segments:
        total += 10 + cv.text_w("%s %d" % (label, count), 1) + 12
    cx = 512 - total // 2
    cv.fill(14, y, 996, 18, INK)
    for label, count in segments:
        cv.fill(cx, y + 5, 8, 8, colors.get(label, GOLD))
        cx += 10
        cx = cv.text(cx, y + 5, "%s %d" % (label, count), PAPER, 1)
        cx += 12


def draw():
    assert len(CARDS) == 13 and len(BRIEFS) == 29
    assert len(CARDS) + len(BRIEFS) == 42
    cv = Canvas(W, H, PAPER)
    cv.box(6, 6, 1012, 1012, INK, 2)
    cv.text_center(512, 22, "THE WORLD TODAY", INK, 6)
    cv.hline(60, 70, 904, INK, 2)
    cv.text_center(512, 78, "SUNDAY - 22 NOVEMBER 2026", INK, 3)
    cv.text_center(512, 104, "42 STORIES - 6 CONTINENTS - 13 ILLUSTRATED", INK, 2)
    # day in numbers
    ny, nh, cw = 126, 46, 166
    for i, (val, lab) in enumerate(NUMBERS):
        cx = 14 + i * cw
        cv.box(cx, ny, cw, nh, INK)
        cv.text_center(cx + cw // 2, ny + 7, val, RED, 2)
        cv.text_center(cx + cw // 2, ny + 29, lab, INK, 1)
    order = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]
    ribbon(cv, 178, [(r, REGION_COUNTS[r]) for r in order if r in REGION_COUNTS],
           REGION_COLOR)
    fields = ["WAR", "POLITICS", "ECONOMY", "JUSTICE", "CLIMATE", "TECH",
              "CULTURE", "SCIENCE", "SOCIETY", "HEALTH", "DISASTER", "SPORT"]
    ribbon(cv, 198, [(f, FIELD_COUNTS[f]) for f in fields if f in FIELD_COUNTS],
           {})
    # cards: row 1 of 3, rows 2-3 of 5
    row1 = CARDS[0:3]
    w1 = (996 - 16) // 3
    for i, card in enumerate(row1):
        draw_card(cv, 14 + i * (w1 + 8), 224, w1, 178, card)
    w2 = (996 - 32) // 5
    for r, row in enumerate((CARDS[3:8], CARDS[8:13])):
        for i, card in enumerate(row):
            draw_card(cv, 14 + i * (w2 + 8), 410 + r * 176, w2, 168, card)
    # bottom: map left, briefs right
    draw_map(cv, 14, 762, 330, 190)
    cv.text(352, 764, "ALSO ON SUNDAY 22 NOVEMBER - SOURCES: REUTERS, AP, AFP, BBC, AL JAZEERA, AAP", INK, 1)
    cv.hline(352, 778, 658, INK, 1)
    for col, group in enumerate((BRIEFS[0:15], BRIEFS[15:29])):
        bx = 352 + col * 336
        for j, (num, region, field, text) in enumerate(group):
            by = 786 + j * 11
            cv.text(bx, by, "%d." % num, RED, 1)
            cv.text(bx + 18, by, text, INK, 1)
    # date check
    cv.box(14, 960, 996, 48, RED, 2)
    dlines = cv.wrap(DATE_CHECK, (996 - 20) // 6)
    for i, ln in enumerate(dlines[:3]):
        cv.text(22, 968 + i * 11, ln, RED, 1)
    return cv


def main():
    cv = draw()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    data = png_bytes(cv)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(data)
    print("wrote %d bytes" % len(data))


if __name__ == "__main__":
    main()
