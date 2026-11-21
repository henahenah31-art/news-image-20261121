# The World Today — Saturday, 21 November 2026
# makefun anchor 6f78051b43408070770d12b6c516101947a19285 round 34141363
#
# Draws one newspaper front page summing up the world's news of
# Saturday 21 November 2026 and writes it to /output/entry.png
# (or $MAKEFUN_OUTPUT_DIR / $ENTRY_OUTPUT when set).
#
# PURE PYTHON STDLIB ONLY: imports are math, os, struct, sys, zlib.
# No third-party imaging, no font files, no network, no clock, no randomness.
# The PNG encoder (zlib + struct), the 5x7 bitmap font, the text
# wrapper, and every shape (rects, lines, circles, icons) are written
# here from scratch, so the program runs in a bare python3 image.
# The same input always produces a byte-identical PNG. Every story on
# the page happened, or was first reported, on 21 November 2026;
# Friday's big stories (Poland missiles, ICJ Myanmar ruling, GTA VI
# $3.79bn, Bolsonaro hospital, NSE 5th-largest, WFP appeal, Sydney
# terror plot, Kryvyi Rih toll, COP31 Friday draft) were checked and
# left out.

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024
MARGIN = 28
CONTENT_W = W - 2 * MARGIN

PAPER = (253, 252, 246)
INK = (20, 20, 20)
GREY = (102, 102, 102)
LIGHT_GREY = (200, 200, 192)
RED = (163, 22, 33)
NAVY = (31, 58, 95)
NAVY_LIGHT = (207, 216, 227)
TEAL = (14, 110, 110)
ORANGE = (196, 94, 10)
GREEN = (34, 120, 60)
GOLD = (212, 160, 23)
SKY = (178, 216, 235)
WHITE = (255, 255, 255)
BLUE = (30, 110, 180)

# ---------------------------------------------------------------- font
# Hand-drawn 5x7 bitmap font. Each glyph is 7 rows of 5 bits ("1" = ink).
# Scale 1 = 7 px tall, advance 6 px; scale N multiplies both.
FONT = {
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
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "`": ("01000", "00100", "00010", "00000", "00000", "00000", "00000"),
    "{": ("00010", "00100", "00100", "01100", "00100", "00100", "00010"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "}": ("01000", "00100", "00100", "00110", "00100", "00100", "01000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    """1024x1024 RGB pixel buffer with tiny drawing primitives."""

    def __init__(self):
        self.px = bytearray([PAPER[0], PAPER[1], PAPER[2]]) * (W * H)

    def set_px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def hline(self, x0, x1, y, color):
        if y < 0 or y >= H:
            return
        if x0 > x1:
            x0, x1 = x1, x0
        x0 = max(x0, 0)
        x1 = min(x1, W - 1)
        for x in range(x0, x1 + 1):
            i = (y * W + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def vline(self, x, y0, y1, color):
        if x < 0 or x >= W:
            return
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(max(y0, 0), min(y1, H - 1) + 1):
            i = (y * W + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            self.hline(x, x + w - 1, yy, color)

    def rect(self, x, y, w, h, color, width=1):
        for t in range(width):
            self.hline(x, x + w - 1, y + t, color)
            self.hline(x, x + w - 1, y + h - 1 - t, color)
            self.vline(x + t, y, y + h - 1, color)
            self.vline(x + w - 1 - t, y, y + h - 1, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if width <= 1:
                self.set_px(x0, y0, color)
            else:
                r = width // 2
                self.fill_rect(x0 - r, y0 - r, width, width, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, pts, color, width=1):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color, width)

    def fill_polygon(self, pts, color):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(math.ceil(xs[i])), int(math.floor(xs[i + 1])),
                           y, color)

    def filled_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def circle(self, cx, cy, r, color, width=1):
        step = 2 if r > 12 else 3
        for deg in range(0, 360, step):
            a = math.radians(deg)
            x = int(round(cx + r * math.cos(a)))
            y = int(round(cy + r * math.sin(a)))
            if width <= 1:
                self.set_px(x, y, color)
            else:
                self.fill_rect(x - 1, y - 1, width, width, color)

    def filled_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for deg in range(0, 360, 2):
            a = math.radians(deg)
            self.set_px(int(round(cx + rx * math.cos(a))),
                        int(round(cy + ry * math.sin(a))), color)

    def arc(self, cx, cy, r, a0, a1, color, width=2):
        pts = []
        a = a0
        while a <= a1:
            rad = math.radians(a)
            pts.append((int(round(cx + r * math.cos(rad))),
                        int(round(cy + r * math.sin(rad)))))
            a += 4
        self.polyline(pts, color, width)

    # ---- text
    def draw_char(self, glyph, x, y, scale, color):
        for ri, row in enumerate(glyph):
            for ci, bit in enumerate(row):
                if bit == "1":
                    self.fill_rect(x + ci * scale, y + ri * scale,
                                   scale, scale, color)

    def text(self, s, x, y, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                raise SystemExit("no glyph for %r in %r" % (ch, s))
            self.draw_char(glyph, cx, y, scale, color)
            cx += 6 * scale
        return cx

    def text_centered(self, s, cx, y, scale, color):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, color)


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                if text_width(word, scale) > max_w:
                    raise SystemExit("WORD TOO LONG: %r" % word)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def fit_lines(text, scale, max_w, max_lines, label):
    lines = wrap(text, scale, max_w)
    if len(lines) > max_lines:
        raise SystemExit(
            "TEXT TOO LONG (%s): %d lines, max %d: %r"
            % (label, len(lines), max_lines, text))
    return lines


def text_block(c, lines, scale, x, y, color, leading):
    for line in lines:
        c.text(line, x, y, scale, color)
        y += leading
    return y


# ---------------------------------------------------------------- PNG
def png_bytes(c):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += c.px[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- stories
# Eight main stories. Each: kicker, headline, summary, icon key.
MAINS = [
    {
        "kicker": "CLIMATE - ANTALYA, TURKIYE",
        "headline": "COP31 spills into Saturday overtime",
        "summary": (
            "Negotiators miss the Friday deadline as nearly 200 nations stay in "
            "Antalya into Saturday, still split over fossil-fuel language and a "
            "\"35 by 35\" electrification goal. A Panama-led bloc calls the draft "
            "\"not good enough\"."
        ),
        "icon": "globe",
    },
    {
        "kicker": "WEATHER - ODISHA, INDIA",
        "headline": "Akvan: the morning after",
        "summary": (
            "Rain lingers over Odisha as relief teams clear roads and restore "
            "power. Schools stay shut today and fishermen must stay ashore. "
            "372,000 evacuated; no deaths reported."
        ),
        "icon": "cyclone",
    },
    {
        "kicker": "AUSTRALIA - NEW SOUTH WALES",
        "headline": "Boy, 3, killed at holiday park",
        "summary": (
            "A three-year-old boy dies after being hit by a car at a holiday park "
            "on the NSW Central Coast on Saturday morning, in the first hours of "
            "the weekend."
        ),
        "icon": "caravan",
    },
    {
        "kicker": "AUSTRALIA - CRIME",
        "headline": "Teens hurt in saw-blade mall fight",
        "summary": (
            "Teenagers are rushed to hospital after circular saw blades are used "
            "in a fight at a shopping centre on Saturday."
        ),
        "icon": "saw",
    },
    {
        "kicker": "DIPLOMACY - APEC",
        "headline": "Three nations, one APEC message",
        "summary": (
            "Australia, Canada and New Zealand issue a joint statement on the "
            "APEC meetings, dated 21 November, backing peace, stability and open "
            "trade across the Pacific."
        ),
        "icon": "flags",
    },
    {
        "kicker": "WEATHER - STORM XAVIER",
        "headline": "Xavier: gale warning narrowed",
        "summary": (
            "A new marine gale warning issued early on Saturday narrows the area "
            "where winds above 33 knots are expected from Storm Xavier."
        ),
        "icon": "waves",
    },
    {
        "kicker": "EDUCATION - INDIA",
        "headline": "Exam results day in India",
        "summary": (
            "The IBPS posts the status of its PO mains result and the Medical "
            "Counselling Committee releases the NEET PG 2026 round-two provisional "
            "allotment, both on Saturday."
        ),
        "icon": "exam",
    },
    {
        "kicker": "BUSINESS - INDIA",
        "headline": "India's energy day",
        "summary": (
            "Coal auctions draw 85 bids for 18 blocks; the atomic regulator clears "
            "the first approach to criticality at a 700 MW Rajasthan reactor; NLC "
            "India Renewables files papers for a Rs 3,300-crore IPO."
        ),
        "icon": "bolt",
    },
]

# Thirty briefs. Each must fit one line in its column.
BRIEFS = [
    "COP31: France, Panama lead bloc demanding fossil-fuel language",
    "COP31 draft drops the $120bn adaptation-finance target",
    "COP31: the Caretta turtle mascot lies dismantled backstage",
    "Akvan: orange alert for very heavy rain in 14 districts",
    "Akvan: 423 rescue teams deployed; 9,341 shelters readied",
    "Akvan: 209 mm of rain at Patrapur, the heaviest in Odisha",
    "Cricket: day three of the Wellington Test starts today; India 159/1",
    "F1: Las Vegas Grand Prix qualifying under the lights tonight",
    "Nepal PM Balendra Shah flies to Delhi tomorrow for a two-day visit",
    "Pakistan climate minister in Delhi for the SCO dialogue forum",
    "Japan's forces to use Indian facilities for live-fire drills, a first",
    "REC wins three awards at a legal and compliance summit",
    "NHPC gets the nod to merge its Jalpower subsidiary",
    "POWERGRID to sell its CTUIL stake to GRID-INDIA for Rs 73.46 cr",
    "CERC clears 1,050 MW of NHPC green capacity at Rs 4.48 a unit",
    "Tata Power-DDL issues 4,071 safety notices near power lines",
    "Minister: excise cuts kept fuel affordable amid global turmoil",
    "Biodiesel blending just 0.08% in April-September, oil firms say",
    "New BS-VI vehicles may get up to three-year pollution certificates",
    "India's crude import bill jumps 88% to $19.5bn in October",
    "DVC holds a state painting contest; SJVN winners felicitated",
    "Bird flu reaches a remote Australian wildlife sanctuary",
    "Smelter future secured with a $200m rescue package",
    "David Jones axes 1,680 staff before Christmas",
    "More Aussies swap sleep-ins for 5am starts, 'dawn-maxxing'",
    "Elton John lets rip at the Australian prime minister",
    "Medicare breach review urges AI staff swaps with tech firms",
    "Hyundai shows new hybrid tech at the Los Angeles Auto Show",
    "ASX ends its worst week since Covid as the AI sell-off rolls on",
    "Wreck of first Australian warship found",
]

NUMBERS = [
    ("38", "stories in this edition"),
    ("200", "nations at COP31"),
    ("372,000", "people evacuated"),
    ("209 mm", "heaviest rain, Patrapur"),
    ("85", "bids for 18 coal blocks"),
    ("1,050 MW", "green capacity cleared"),
]

FOOTER_1 = (
    "EARLY EDITION - News reported up to about 03:00 UTC (10:00 WIB), "
    "Saturday 21 November 2026."
)
FOOTER_2 = (
    "Every story happened, or was first reported, on 21 November 2026. "
    "Later: COP31 overtime, day three in Wellington, Las Vegas GP qualifying."
)


# ---------------------------------------------------------------- icons
def icon_globe(c, x, y, s):
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 4
    c.filled_circle(cx, cy, r, SKY)
    c.circle(cx, cy, r, NAVY, 2)
    c.ellipse(cx, cy, r, r // 2, NAVY)
    c.ellipse(cx, cy, r // 2, r, NAVY)
    c.hline(cx - r, cx + r, cy, NAVY)


def icon_thermo(c, x, y, s):
    mid = x + s // 2
    c.fill_rect(mid - 5, y + 4, 11, s - 16, (255, 235, 235))
    c.rect(mid - 5, y + 4, 11, s - 16, RED, 2)
    c.filled_circle(mid, y + s - 12, 9, RED)
    c.vline(mid, y + 10, y + s - 12, RED)
    c.vline(mid - 1, y + 10, y + s - 12, RED)
    c.vline(mid + 1, y + 10, y + s - 12, RED)


def icon_cyclone(c, x, y, s):
    cx, cy = x + s // 2, y + s // 2 - 4
    for k, rad in enumerate((26, 20, 14, 8)):
        a0 = 30 + k * 55
        c.arc(cx, cy, rad, a0, a0 + 250, TEAL, 3)
    for dx in (-16, 0, 16):
        c.vline(cx + dx, y + s - 12, y + s - 4, TEAL)


def icon_caravan(c, x, y, s):
    c.fill_polygon([(x + 4, y + s - 14), (x + 16, y + 6),
                    (x + 28, y + s - 14)], GREEN)
    c.fill_rect(x + 13, y + s - 14, 7, 8, (120, 72, 20))
    c.fill_rect(x + 32, y + 18, s - 36, s - 34, (150, 200, 235))
    c.rect(x + 32, y + 18, s - 36, s - 34, NAVY, 2)
    for wx in (x + 40, x + s - 14):
        c.filled_circle(wx, y + s - 12, 4, INK)


def icon_saw(c, x, y, s):
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 8
    pts = []
    for i in range(24):
        ang = math.pi * 2 * i / 24
        rr = r if i % 2 == 0 else r - 7
        pts.append((int(round(cx + rr * math.cos(ang))),
                    int(round(cy + rr * math.sin(ang)))))
    c.fill_polygon(pts, (180, 180, 180))
    c.circle(cx, cy, r - 8, GREY, 1)
    c.filled_circle(cx, cy, 4, INK)


def icon_flags(c, x, y, s):
    cols = [RED, NAVY, GREEN]
    for i, col in enumerate(cols):
        px = x + 8 + i * (s - 16) // 2
        c.vline(px, y + 6, y + s - 8, INK)
        c.vline(px + 1, y + 6, y + s - 8, INK)
        c.fill_polygon([(px, y + 6), (px + 16, y + 10), (px, y + 16)], col)


def icon_waves(c, x, y, s):
    for row, yy in enumerate((y + 12, y + 26, y + 40)):
        pts = []
        for t in range(0, s + 1, 4):
            pts.append((x + t, yy + int(round(4 * math.sin(t / 9.0 + row)))))
        c.polyline(pts, BLUE, 3)
    c.filled_circle(x + s - 13, y + s - 8, 7, GOLD)


def icon_exam(c, x, y, s):
    c.fill_rect(x + 10, y + 6, s - 20, s - 12, WHITE)
    c.rect(x + 10, y + 6, s - 20, s - 12, INK, 2)
    c.fill_polygon([(x + s - 10, y + 6), (x + s - 22, y + 6),
                    (x + s - 10, y + 18)], LIGHT_GREY)
    for yy in (y + 20, y + 28, y + 36):
        c.hline(x + 16, x + s - 20, yy, GREY)
        c.hline(x + 16, x + s - 20, yy + 1, GREY)
    c.polyline([(x + 16, y + s - 14), (x + 22, y + s - 8),
                (x + 32, y + s - 20)], RED, 3)


def icon_bolt(c, x, y, s):
    c.fill_polygon([(x + s // 2 + 6, y + 4),
                    (x + s // 2 - 12, y + s // 2 + 2),
                    (x + s // 2 - 1, y + s // 2 + 2),
                    (x + s // 2 - 6, y + s - 4),
                    (x + s // 2 + 12, y + s // 2 - 2),
                    (x + s // 2 + 1, y + s // 2 - 2)], GOLD)


ICONS = {
    "globe": icon_globe,
    "cyclone": icon_cyclone,
    "caravan": icon_caravan,
    "saw": icon_saw,
    "flags": icon_flags,
    "waves": icon_waves,
    "exam": icon_exam,
    "bolt": icon_bolt,
}


# ---------------------------------------------------------------- page
def draw_page():
    c = Canvas()

    # ---- masthead
    title = "THE WORLD TODAY"
    c.text(title, (W - text_width(title, 5)) // 2, 16, 5, INK)
    c.fill_rect(MARGIN, 58, CONTENT_W, 3, INK)
    c.fill_rect(MARGIN, 63, CONTENT_W, 1, INK)
    left = "SATURDAY, 21 NOVEMBER 2026"
    right = "EARLY EDITION - 38 STORIES"
    c.text(left, MARGIN, 70, 2, INK)
    c.text(right, W - MARGIN - text_width(right, 2), 70, 2, RED)

    # ---- lead story (main 1)
    lead = MAINS[0]
    ly0, ly1 = 92, 250
    c.rect(MARGIN, ly0, CONTENT_W, ly1 - ly0, LIGHT_GREY, 1)
    c.fill_rect(MARGIN, ly0, 4, ly1 - ly0, RED)
    tx = MARGIN + 16
    c.text(lead["kicker"], tx, ly0 + 8, 2, RED)
    head_lines = fit_lines(lead["headline"], 3, 668, 2, "lead headline")
    y = text_block(c, head_lines, 3, tx, ly0 + 30, INK, 26)
    body_lines = fit_lines(lead["summary"], 2, 668, 5, "lead summary")
    text_block(c, body_lines, 2, tx, y + 6, INK, 18)
    # lead illustration: globe + thermometer + "35 by 35"
    icon_globe(c, 740, ly0 + 10, 96)
    icon_thermo(c, 872, ly0 + 24, 80)
    c.text_centered("35 BY 35", 788, ly0 + 114, 2, TEAL)
    c.text_centered("GOAL", 912, ly0 + 114, 2, GREY)

    # ---- mains grid: stories 2..7 in 2 columns x 3 rows
    cell_w, cell_h = 476, 108
    gap_x, gap_y = 16, 8
    grid_y0 = 258
    for idx, story in enumerate(MAINS[1:7]):
        row, col = divmod(idx, 2)
        cx0 = MARGIN + col * (cell_w + gap_x)
        cy0 = grid_y0 + row * (cell_h + gap_y)
        c.rect(cx0, cy0, cell_w, cell_h, LIGHT_GREY, 1)
        ICONS[story["icon"]](c, cx0 + 6, cy0 + 24, 58)
        tx = cx0 + 72
        c.text(story["kicker"], tx, cy0 + 6, 2, RED)
        h_lines = fit_lines(story["headline"], 2, cell_w - 80, 2,
                            "headline " + story["headline"])
        text_block(c, h_lines, 2, tx, cy0 + 24, INK, 17)
        b_lines = fit_lines(story["summary"], 1, cell_w - 80, 3,
                            "summary " + story["headline"])
        text_block(c, b_lines, 1, tx, cy0 + 62, INK, 11)

    # ---- full-width main 8
    fw = MAINS[7]
    fy0, fy1 = 606, 712
    c.rect(MARGIN, fy0, CONTENT_W, fy1 - fy0, LIGHT_GREY, 1)
    c.fill_rect(MARGIN, fy0, 4, fy1 - fy0, RED)
    ICONS[fw["icon"]](c, MARGIN + 12, fy0 + 12, 64)
    tx = MARGIN + 88
    c.text(fw["kicker"], tx, fy0 + 8, 2, RED)
    c.text(fw["headline"], tx, fy0 + 26, 2, INK)
    b_lines = fit_lines(fw["summary"], 2, W - 2 * MARGIN - 104, 3,
                        "summary wide")
    text_block(c, b_lines, 2, tx, fy0 + 50, INK, 18)

    # ---- briefs
    by0 = 720
    c.text("THE DAY IN BRIEF", MARGIN, by0, 2, INK)
    count = "%d MORE STORIES" % len(BRIEFS)
    c.text(count, W - MARGIN - text_width(count, 2), by0, 2, RED)
    c.fill_rect(MARGIN, by0 + 22, CONTENT_W, 2, INK)
    col_w = 472
    for i, brief in enumerate(BRIEFS):
        col, row = divmod(i, 15)
        bx = MARGIN + col * (col_w + 24)
        by = by0 + 28 + row * 12
        if text_width(brief, 1) > col_w - 14:
            raise SystemExit("BRIEF TOO LONG (%d chars): %r"
                             % (len(brief), brief))
        c.fill_rect(bx, by + 1, 5, 5, RED)
        c.text(brief, bx + 12, by, 1, INK)

    # ---- by the numbers
    c.text("BY THE NUMBERS", MARGIN, 930, 2, NAVY)
    ny0, ny1 = 948, 988
    c.fill_rect(MARGIN, ny0, CONTENT_W, ny1 - ny0, NAVY)
    seg_w = CONTENT_W // len(NUMBERS)
    for i, (val, lab) in enumerate(NUMBERS):
        cx = MARGIN + seg_w * i + seg_w // 2
        c.text_centered(val, cx, ny0 + 4, 2, WHITE)
        c.text_centered(lab, cx, ny0 + 24, 1, NAVY_LIGHT)
        if i:
            c.vline(MARGIN + seg_w * i, ny0 + 6, ny1 - 6, (90, 110, 140))

    # ---- footer
    c.text_centered(FOOTER_1, W // 2, 994, 1, GREY)
    c.text_centered(FOOTER_2, W // 2, 1006, 1, GREY)

    return c


def check_glyphs():
    texts = [FOOTER_1, FOOTER_2, "THE WORLD TODAY",
             "SATURDAY, 21 NOVEMBER 2026", "EARLY EDITION - 38 STORIES",
             "THE DAY IN BRIEF", "BY THE NUMBERS", "35 BY 35", "GOAL"]
    for story in MAINS:
        texts += [story["kicker"], story["headline"], story["summary"]]
    texts += BRIEFS
    for val, lab in NUMBERS:
        texts += [val, lab]
    for t in texts:
        for ch in t:
            if ch not in FONT:
                raise SystemExit("no glyph for %r in %r" % (ch, t))


def main():
    if len(MAINS) != 8:
        raise SystemExit("need 8 mains, have %d" % len(MAINS))
    if len(BRIEFS) != 30:
        raise SystemExit("need 30 briefs, have %d" % len(BRIEFS))
    check_glyphs()
    out_dir = (
        os.environ.get("MAKEFUN_OUTPUT_DIR")
        or os.environ.get("ENTRY_OUTPUT")
        or "/output"
    )
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(draw_page())
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))
    print("stories: %d mains + %d briefs = %d"
          % (len(MAINS), len(BRIEFS), len(MAINS) + len(BRIEFS)))


if __name__ == "__main__":
    main()
