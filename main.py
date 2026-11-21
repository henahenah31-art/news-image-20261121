# The World Today — Saturday, 21 November 2026
# makefun anchor 6f78051b43408070770d12b6c516101947a19285 round 34141363
#
# Draws one newspaper front page summing up the world's news of
# Saturday 21 November 2026 and writes it to /output/entry.png
# (or $MAKEFUN_OUTPUT_DIR / $ENTRY_OUTPUT when set).
#
# Pure Python + Pillow, no network, no clock, no randomness: the same
# input always produces a byte-identical PNG. Every story on the page
# happened, or was first reported, on 21 November 2026; Friday's big
# stories (Poland missiles, ICJ Myanmar ruling, GTA VI $3.79bn,
# Bolsonaro hospital, NSE 5th-largest, WFP appeal, Sydney terror
# plot, Kryvyi Rih toll, COP31 Friday draft) were checked and left out.

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

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

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(round(size)))


F_TITLE = font(SERIF_B, 52)
F_DATE = font(SANS_B, 14)
F_KICKER = font(SANS_B, 12)
F_KICKER_SM = font(SANS_B, 10.5)
F_LEAD_HEAD = font(SERIF_B, 27)
F_HEAD = font(SERIF_B, 16)
F_HEAD_WIDE = font(SERIF_B, 17)
F_LEAD_BODY = font(SANS, 15)
F_BODY = font(SANS, 12.5)
F_BODY_WIDE = font(SANS, 13)
F_BRIEF = font(SANS, 12)
F_SECTION = font(SANS_B, 14)
F_NUM = font(SANS_B, 16)
F_NUMLAB = font(SANS, 9.5)
F_FOOT = font(SANS, 10.5)
F_ICON_TXT = font(SANS_B, 13)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if fnt.getlength(trial) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def fit_lines(text, fnt, max_w, max_lines, label):
    lines = wrap(text, fnt, max_w)
    if len(lines) > max_lines:
        raise SystemExit(
            "TEXT TOO LONG (%s): %d lines, max %d: %r" % (label, len(lines), max_lines, text)
        )
    return lines


def text_block(draw, lines, fnt, x, y, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- stories
# Eight main stories. Each: kicker, headline, summary, icon key.
MAINS = [
    {
        "kicker": "CLIMATE \u2014 ANTALYA, TURKIYE",
        "headline": "COP31 spills into Saturday overtime",
        "summary": (
            "Negotiators miss the Friday deadline as nearly 200 nations stay in "
            "Antalya into Saturday, still split over fossil-fuel language and a "
            "\u201c35 by 35\u201d electrification goal. A Panama-led bloc calls the draft "
            "\u201cnot good enough\u201d."
        ),
        "icon": "globe",
    },
    {
        "kicker": "WEATHER \u2014 ODISHA, INDIA",
        "headline": "Akvan: the morning after",
        "summary": (
            "Rain lingers over Odisha as relief teams clear roads and restore "
            "power. Schools stay shut today and fishermen must stay ashore. "
            "372,000 evacuated; no deaths reported."
        ),
        "icon": "cyclone",
    },
    {
        "kicker": "AUSTRALIA \u2014 NEW SOUTH WALES",
        "headline": "Boy, 3, killed at holiday park",
        "summary": (
            "A three-year-old boy dies after being hit by a car at a holiday park "
            "on the NSW Central Coast on Saturday morning, in the first hours of "
            "the weekend."
        ),
        "icon": "caravan",
    },
    {
        "kicker": "AUSTRALIA \u2014 CRIME",
        "headline": "Teens hurt in saw-blade mall fight",
        "summary": (
            "Teenagers are rushed to hospital after circular saw blades are used "
            "in a fight at a shopping centre on Saturday."
        ),
        "icon": "saw",
    },
    {
        "kicker": "DIPLOMACY \u2014 APEC",
        "headline": "Three nations, one APEC message",
        "summary": (
            "Australia, Canada and New Zealand issue a joint statement on the "
            "APEC meetings, dated 21 November, backing peace, stability and open "
            "trade across the Pacific."
        ),
        "icon": "flags",
    },
    {
        "kicker": "WEATHER \u2014 STORM XAVIER",
        "headline": "Xavier: gale warning narrowed",
        "summary": (
            "A new marine gale warning issued early on Saturday narrows the area "
            "where winds above 33 knots are expected from Storm Xavier."
        ),
        "icon": "waves",
    },
    {
        "kicker": "EDUCATION \u2014 INDIA",
        "headline": "Exam results day in India",
        "summary": (
            "The IBPS posts the status of its PO mains result and the Medical "
            "Counselling Committee releases the NEET PG 2026 round-two provisional "
            "allotment, both on Saturday."
        ),
        "icon": "exam",
    },
    {
        "kicker": "BUSINESS \u2014 INDIA",
        "headline": "India\u2019s energy day",
        "summary": (
            "Coal auctions draw 85 bids for 18 blocks; the atomic regulator clears "
            "the first approach to criticality at a 700 MW Rajasthan reactor; NLC "
            "India Renewables files papers for a Rs 3,300-crore IPO."
        ),
        "icon": "bolt",
    },
]

# Thirty one-line briefs. Each must fit one line in its column.
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
    ("372,000", "people evacuated from Akvan"),
    ("209 mm", "heaviest rain, Patrapur"),
    ("85", "bids for 18 coal blocks"),
    ("1,050 MW", "NHPC green capacity cleared"),
]

FOOTER_1 = (
    "EARLY EDITION \u2014 News reported up to about 03:00 UTC (10:00 WIB), "
    "Saturday 21 November 2026."
)
FOOTER_2 = (
    "Every story here happened, or was first reported, on 21 November 2026; "
    "Friday's stories were left out. Later today: COP31 overtime, day three "
    "in Wellington, Las Vegas GP qualifying."
)


# ---------------------------------------------------------------- icons
def icon_globe(d, x, y, s):
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 4
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 216, 235), outline=NAVY, width=2)
    d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], outline=NAVY, width=1)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=NAVY, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=NAVY, width=1)


def icon_thermo(d, x, y, s):
    # small thermometer standing by the globe
    d.rounded_rectangle([x + s // 2 - 5, y + 4, x + s // 2 + 5, y + s - 14],
                        radius=5, outline=RED, width=2, fill=(255, 235, 235))
    d.ellipse([x + s // 2 - 9, y + s - 20, x + s // 2 + 9, y + s - 2],
              fill=RED, outline=RED)
    d.line([x + s // 2, y + 10, x + s // 2, y + s - 12], fill=RED, width=3)


def icon_cyclone(d, x, y, s):
    cx, cy = x + s // 2, y + s // 2 - 4
    for k, rad in enumerate((26, 20, 14, 8)):
        a0 = 30 + k * 55
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], a0, a0 + 250,
              fill=TEAL, width=3)
    for i, dx in enumerate((-16, 0, 16)):
        d.line([cx + dx, y + s - 12, cx + dx, y + s - 4], fill=TEAL, width=2)


def icon_caravan(d, x, y, s):
    d.polygon([(x + 4, y + s - 14), (x + 16, y + 6), (x + 28, y + s - 14)],
              fill=GREEN)
    d.rectangle([x + 13, y + s - 14, x + 19, y + s - 6], fill=(120, 72, 20))
    d.rounded_rectangle([x + 32, y + 18, x + s - 4, y + s - 16], radius=4,
                        fill=(150, 200, 235), outline=NAVY, width=2)
    for wx in (x + 40, x + s - 14):
        d.ellipse([wx - 4, y + s - 16, wx + 4, y + s - 8], fill=INK)


def icon_saw(d, x, y, s):
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 8
    pts = []
    for i in range(24):
        ang = math.pi * 2 * i / 24
        rr = r if i % 2 == 0 else r - 7
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=(180, 180, 180), outline=GREY)
    d.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8],
              fill=(220, 220, 220), outline=GREY)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)


def icon_flags(d, x, y, s):
    cols = [RED, NAVY, GREEN]
    for i, col in enumerate(cols):
        px = x + 8 + i * (s - 16) // 2
        d.line([px, y + 6, px, y + s - 8], fill=INK, width=2)
        d.polygon([(px, y + 6), (px + 16, y + 10), (px, y + 16)], fill=col)


def icon_waves(d, x, y, s):
    for row, yy in enumerate((y + 12, y + 26, y + 40)):
        pts = []
        for t in range(0, s + 1, 4):
            pts.append((x + t, yy + 4 * math.sin(t / 9.0 + row)))
        d.line(pts, fill=(30, 110, 180), width=3)
    d.ellipse([x + s - 20, y + s - 14, x + s - 6, y + s - 2], fill=GOLD)


def icon_exam(d, x, y, s):
    d.rectangle([x + 10, y + 6, x + s - 10, y + s - 6], fill=(255, 255, 255),
                outline=INK, width=2)
    d.polygon([(x + s - 10, y + 6), (x + s - 22, y + 6), (x + s - 10, y + 18)],
              fill=LIGHT_GREY, outline=INK)
    for i, yy in enumerate((y + 20, y + 28, y + 36)):
        d.line([x + 16, yy, x + s - 20, yy], fill=GREY, width=2)
    d.line([(x + 16, y + s - 14), (x + 22, y + s - 8), (x + 32, y + s - 20)],
           fill=RED, width=3)


def icon_bolt(d, x, y, s):
    d.polygon([(x + s // 2 + 6, y + 4), (x + s // 2 - 12, y + s // 2 + 2),
               (x + s // 2 - 1, y + s // 2 + 2), (x + s // 2 - 6, y + s - 4),
               (x + s // 2 + 12, y + s // 2 - 2), (x + s // 2 + 1, y + s // 2 - 2)],
              fill=GOLD, outline=ORANGE)
    d.ellipse([x + 4, y + s - 12, x + 14, y + s - 2], fill=INK)
    d.ellipse([x + s - 16, y + s - 12, x + s - 6, y + s - 2], fill=INK)


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
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    title = "THE WORLD TODAY"
    tw = F_TITLE.getlength(title)
    d.text(((W - tw) / 2, 14), title, font=F_TITLE, fill=INK)
    d.rectangle([MARGIN, 78, W - MARGIN, 81], fill=INK)
    d.rectangle([MARGIN, 84, W - MARGIN, 85], fill=INK)
    left = "SATURDAY, 21 NOVEMBER 2026"
    right = "EARLY EDITION \u2014 38 STORIES"
    d.text((MARGIN, 92), left, font=F_DATE, fill=INK)
    rw = F_DATE.getlength(right)
    d.text((W - MARGIN - rw, 92), right, font=F_DATE, fill=RED)

    # ---- lead story (main 1)
    lead = MAINS[0]
    ly0, ly1 = 118, 266
    d.rectangle([MARGIN, ly0, W - MARGIN, ly1], outline=LIGHT_GREY, width=1)
    d.rectangle([MARGIN, ly0, MARGIN + 4, ly1], fill=RED)
    tx = MARGIN + 16
    d.text((tx, ly0 + 8), lead["kicker"], font=F_KICKER, fill=RED)
    head_lines = fit_lines(lead["headline"], F_LEAD_HEAD, 668, 2, "lead headline")
    y = text_block(d, head_lines, F_LEAD_HEAD, tx, ly0 + 24, INK, 30)
    body_lines = fit_lines(lead["summary"], F_LEAD_BODY, 668, 3, "lead summary")
    text_block(d, body_lines, F_LEAD_BODY, tx, y + 4, INK, 18)
    # lead illustration: globe + thermometer + "35 by 35"
    icon_globe(d, 748, ly0 + 10, 92)
    icon_thermo(d, 884, ly0 + 22, 76)
    tag = "35 BY 35"
    tgw = F_ICON_TXT.getlength(tag)
    d.text((748 + (92 - tgw) / 2, ly0 + 108), tag, font=F_ICON_TXT, fill=TEAL)
    d.text((884, ly0 + 108), "GOAL", font=F_ICON_TXT, fill=GREY)

    # ---- mains grid: stories 2..7 in 2 columns x 3 rows
    cell_w, cell_h = 476, 102
    gap_x, gap_y = 16, 8
    grid_y0 = 274
    for idx, story in enumerate(MAINS[1:7]):
        row, col = divmod(idx, 2)
        cx0 = MARGIN + col * (cell_w + gap_x)
        cy0 = grid_y0 + row * (cell_h + gap_y)
        d.rectangle([cx0, cy0, cx0 + cell_w, cy0 + cell_h],
                    outline=LIGHT_GREY, width=1)
        ICONS[story["icon"]](d, cx0 + 6, cy0 + 22, 58)
        tx = cx0 + 72
        d.text((tx, cy0 + 8), story["kicker"], font=F_KICKER_SM, fill=RED)
        h_lines = fit_lines(story["headline"], F_HEAD, cell_w - 80, 1,
                            "headline " + story["headline"])
        y = text_block(d, h_lines, F_HEAD, tx, cy0 + 24, INK, 20)
        b_lines = fit_lines(story["summary"], F_BODY, cell_w - 80, 3,
                            "summary " + story["headline"])
        text_block(d, b_lines, F_BODY, tx, cy0 + 48, INK, 16)

    # ---- full-width main 8
    fw = MAINS[7]
    fy0, fy1 = 604, 688
    d.rectangle([MARGIN, fy0, W - MARGIN, fy1], outline=LIGHT_GREY, width=1)
    d.rectangle([MARGIN, fy0, MARGIN + 4, fy1], fill=RED)
    ICONS[fw["icon"]](d, MARGIN + 12, fy0 + 10, 64)
    tx = MARGIN + 88
    d.text((tx, fy0 + 8), fw["kicker"], font=F_KICKER_SM, fill=RED)
    d.text((tx, fy0 + 24), fw["headline"], font=F_HEAD_WIDE, fill=INK)
    b_lines = fit_lines(fw["summary"], F_BODY_WIDE, W - 2 * MARGIN - 104, 2,
                        "summary wide")
    text_block(d, b_lines, F_BODY_WIDE, tx, fy0 + 48, INK, 17)

    # ---- briefs
    by0 = 696
    d.text((MARGIN, by0), "THE DAY IN BRIEF", font=F_SECTION, fill=INK)
    count = "%d MORE STORIES" % len(BRIEFS)
    cw = F_SECTION.getlength(count)
    d.text((W - MARGIN - cw, by0), count, font=F_SECTION, fill=RED)
    d.rectangle([MARGIN, by0 + 22, W - MARGIN, by0 + 24], fill=INK)
    col_w = 472
    for i, brief in enumerate(BRIEFS):
        col, row = divmod(i, 15)
        bx = MARGIN + col * (col_w + 24)
        by = by0 + 26 + row * 14
        if F_BRIEF.getlength(brief) > col_w - 14:
            raise SystemExit("BRIEF TOO LONG (%d chars): %r" % (len(brief), brief))
        d.text((bx, by), "\u2022", font=F_BRIEF, fill=RED)
        d.text((bx + 12, by), brief, font=F_BRIEF, fill=INK)

    # ---- by the numbers
    d.text((MARGIN, 936), "BY THE NUMBERS", font=F_SECTION, fill=NAVY)
    ny0, ny1 = 952, 992
    d.rectangle([MARGIN, ny0, W - MARGIN, ny1], fill=NAVY)
    seg_w = CONTENT_W / len(NUMBERS)
    for i, (val, lab) in enumerate(NUMBERS):
        cx = MARGIN + seg_w * i + seg_w / 2
        vw = F_NUM.getlength(val)
        d.text((cx - vw / 2, ny0 + 3), val, font=F_NUM, fill=(255, 255, 255))
        lw = F_NUMLAB.getlength(lab)
        d.text((cx - lw / 2, ny0 + 21), lab, font=F_NUMLAB, fill=NAVY_LIGHT)
        if i:
            d.line([MARGIN + seg_w * i, ny0 + 6, MARGIN + seg_w * i, ny1 - 6],
                   fill=(90, 110, 140), width=1)

    # ---- footer
    f1w = F_FOOT.getlength(FOOTER_1)
    d.text(((W - f1w) / 2, 998), FOOTER_1, font=F_FOOT, fill=GREY)
    f2w = F_FOOT.getlength(FOOTER_2)
    d.text(((W - f2w) / 2, 1010), FOOTER_2, font=F_FOOT, fill=GREY)

    return img


def main():
    if len(MAINS) != 8:
        raise SystemExit("need 8 mains, have %d" % len(MAINS))
    if len(BRIEFS) != 30:
        raise SystemExit("need 30 briefs, have %d" % len(BRIEFS))
    out_dir = (
        os.environ.get("MAKEFUN_OUTPUT_DIR")
        or os.environ.get("ENTRY_OUTPUT")
        or "/output"
    )
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img = draw_page()
    if img.size != (1024, 1024):
        raise SystemExit("bad size %r" % (img.size,))
    img.save(path, format="PNG")
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))
    print("stories: %d mains + %d briefs = %d"
          % (len(MAINS), len(BRIEFS), len(MAINS) + len(BRIEFS)))


if __name__ == "__main__":
    main()
