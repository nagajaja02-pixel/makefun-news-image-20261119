#!/usr/bin/env python3
"""Draw 'THE WORLD IN ONE DAY - THURSDAY 19 NOVEMBER 2026' as an editorial
news magazine cover page, v3 (MAJOR VISUAL UPGRADE). Everything is drawn in
code with Pillow. No photos, no network, no fonts beyond the families shipped
on the machine. Deterministic output.

v3 vs v2 - what changed and why (weaknesses found against the top entries):
- v2 read like a dense table: every story in a similar box, similar type,
  similar weight; the eye had nowhere to land first. Rank 1-4 all have one
  huge visual moment, a strict type scale, and a lot of air. v3 rebuilds the
  page as a magazine: 3 large feature panels with rich illustrations, a
  second tier of 8 medium features, and the rest as a quiet index.
- Heroes are now UNEQUAL (summit widest) and their illustrations are far
  richer: vertical gradients for sky/light, layered skyline, shadows under
  the table, glowing dots on the chart, a proper Peace Palace with steps.
- The 7 region chips (a table-like strip) are gone; regions are now one
  small caps line under the sub-headline. The stat strip is slimmed to a
  single row with no box borders, just numbers + labels on the paper.
- Second tier grows from 6 cramped cells to 8 real medium features (2 rows
  of 4), promoting the two strongest list stories: GAZA #10 (IDF ends
  Nuseirat raid) and SHENZHEN #25 (APEC adopts Shenzhen Declaration).
- The index is the remaining 26 stories in 2 columns, deliberately smaller
  and quieter than the features above it.
- The map is now a dark navy feature panel (like the strongest top entry),
  with tan land, red pins and white numbers, and a clear header.
- All 37 stories keep their verified facts, dates, numbers and sources.
  Nothing was invented, nothing was moved to another date. The 5 stories
  replaced in v2 and the 7 fixes there are carried over unchanged.

v4 FINAL POLISH (same layout, same concept):
- Full fact audit of all 37 stories against live reporting. ONE story was
  wrong-dated and is replaced: HANOI #32 "Russian bombers return to
  Vietnam" (bombers arrived 17 Nov, first reported 18 Nov) becomes
  "Vietnam, Russia deepen energy ties" (Reuters, HANOI, 19 Nov: Putin
  and To Lam agree energy cooperation at APEC, incl. nuclear help).
  MOGADISHU #14 was already the correct 19 Nov story (Somalia expels
  the UAE envoy in 72h, Reuters) - the earlier "AU troops" wording was
  fixed in v3. The 13 previously unverified index items are now all
  verified; Jeffries, Vance, Hemedti and Peshawar are "first reported
  19 Nov" (US-evening events = 19 Nov in Asia) and are kept as such.
- Leaders redrawn as characteristic editorial-vector portraits: Trump
  blond pompadour swept right, Xi neat black side-part, Putin short
  grey-blond with receding temples; eyebrows, nose, lapels, collar,
  distinct ties (Putin navy).
- Index enlarged 10pt -> 11pt with 14px rows and 22px number badges;
  a few headlines shortened a word to fit; map narrowed 360 -> 344px
  to give the index room. Vertical space recovered by trimming the
  masthead/stat/hero/tier gaps, not by shrinking any panel.
- Map: story 36 pin corrected to Nassau Island, northern Cook Islands
  (-165.4, -11.2) - v3 had it at Rarotonga. All crowded badge clusters
  (Europe/Middle East, US East Coast, Shenzhen/Hanoi) re-spread with
  radial leader-line offsets so no two number badges overlap.
- DATE CHECK footer now names the removed Hanoi story (Russian bombers
  in Vietnam, 18 Nov) instead of the Pew item.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "entry.png"

# ---------- palette ----------
IVORY   = (247, 241, 227)   # paper
PAPER2  = (252, 249, 240)   # panel paper
NAVY    = (20, 38, 74)
NAVY2   = (28, 52, 96)
NAVY_D  = (13, 24, 48)     # deep navy (map / chart bg)
RED     = (166, 30, 43)
GOLD    = (185, 138, 30)
GOLD_L  = (212, 175, 55)
INK     = (26, 26, 26)
GREY    = (90, 90, 86)
LGREY   = (120, 118, 110)
SEA     = (214, 228, 232)
LAND    = (222, 205, 160)
LAND2   = (206, 186, 138)
WHITE   = (255, 255, 255)
GREEN   = (46, 125, 50)
TEAL    = (0, 121, 107)
PURPLE  = (106, 27, 154)
ORANGE  = (230, 126, 34)

F_SERIF      = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B    = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF_I    = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
F_SANS       = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B     = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(d, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text(d, xy, s, fnt, fill=INK, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)

def para(d, x, y, lines, fnt, fill=INK, leading=None, anchor="la"):
    """Draw wrapped lines starting at x,y (anchor left-top by default)."""
    lh = leading or int(fnt.size * 1.22)
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=fnt, fill=fill, anchor=anchor)
    return y + len(lines) * lh

def kicker(d, x, y, s, fnt, fill=RED):
    d.text((x, y), s, font=fnt, fill=fill, anchor="la")

def hline(d, x0, x1, y, fill=NAVY, w=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)

def gold_rule(d, x0, x1, y):
    d.line([(x0, y), (x1, y)], fill=GOLD, width=2)
    d.line([(x0, y + 4), (x1, y + 4)], fill=GOLD, width=1)

def lerp(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))

def vgrad(d, x, y, w, h, c_top, c_bot):
    """Vertical gradient: horizontal lines interpolated top -> bottom."""
    if h <= 1:
        d.rectangle([x, y, x + w, y + h], fill=c_top)
        return
    for i in range(h):
        d.line([(x, y + i), (x + w, y + i)], fill=lerp(c_top, c_bot, i / (h - 1)))

def hgrad(d, x, y, w, h, c_left, c_right):
    """Horizontal gradient: vertical lines interpolated left -> right."""
    if w <= 1:
        d.rectangle([x, y, x + w, y + h], fill=c_left)
        return
    for i in range(w):
        d.line([(x + i, y), (x + i, y + h)], fill=lerp(c_left, c_right, i / (w - 1)))

# ---------- data: 37 verified stories (facts unchanged from v2) ----------
# heroes: (kicker, headline, deck, source)
HEROES = [
    ("1 \u00b7 SHENZHEN \u00b7 SUMMIT",
     "Trump, Xi and Putin hold first three-way summit",
     "Three nuclear powers meet at APEC in Shenzhen; arms control tops the agenda.",
     "Reuters \u00b7 AP"),
    ("2 \u00b7 THE HAGUE \u00b7 JUSTICE",
     "World Court: Myanmar committed genocide",
     "The ICJ finds Myanmar guilty of genocide against the Rohingya, 9 votes to 6.",
     "Reuters \u00b7 Al Jazeera"),
    ("3 \u00b7 NEW YORK \u00b7 MARKETS",
     "Anthropic starts trading on Nasdaq",
     "Priced at $83, the Claude maker raised a record $81.3bn; shares close at $97.",
     "NPR \u00b7 Bloomberg"),
]

# tier 2 features (8): (number, kicker, headline, deck, source)
# 4-9 are the v2 grid cards; 10 (Gaza) and 25 (Shenzhen APEC) are promoted
# from the list because they are the strongest remaining verified stories.
TIER2 = [
    (4, "ANTALYA \u00b7 CLIMATE",
     "COP31 draft drops fossil fuels",
     "Revised text cuts the $120bn aid goal.",
     "Reuters"),
    (5, "KYIV \u00b7 WAR",
     "Strikes damage two embassies",
     "Drones hit Kyiv; 1 killed, 5 hurt.",
     "AFP"),
    (6, "CRIMEA \u00b7 WAR",
     "Ukraine hits Kerch Bridge again",
     "Neptune missiles halt trains again.",
     "Euronews"),
    (7, "ODISHA \u00b7 STORM",
     "Cyclone Akvan nears coast",
     "300,000 evacuated; landfall due Friday.",
     "IMD"),
    (8, "COPENHAGEN",
     "Denmark backs Arctic pact 109\u20130",
     "Approves the US deal, more bases.",
     "AP"),
    (9, "WORLDWIDE \u00b7 GAMES",
     "GTA VI goes on sale at last",
     "Unlocks at midnight; $79.99.",
     "Rockstar"),
    (10, "GAZA \u00b7 WAR",
     "IDF ends Nuseirat raid",
     "Road reopens after the operation.",
     "Al Jazeera"),
    (25, "SHENZHEN \u00b7 TRADE",
     "APEC adopts Shenzhen Declaration",
     "Digital trade pact for Asia-Pacific.",
     "AP"),
]

# index: the remaining 26 stories, in number order (place, headline).
# Numbers shown are the original story numbers 1-37, so the map pins match.
INDEX = [
    (11, "GULF", "IEA warns of energy threat as crisis grows."),
    (12, "BAGHDAD", "Iraq, Kataib Hezbollah standoff eases."),
    (13, "PORT SUDAN", "Hemedti's 2nd death sentence."),
    (14, "MOGADISHU", "Somalia expels UAE envoy in 72h."),
    (15, "JOBURG", "Proteas beat Bangladesh by 9 wickets."),
    (16, "ULAANBAATAR", "President quits; vote 96\u2013104."),
    (17, "PESHAWAR", "Pakistan kills 22 militants in raids."),
    (18, "NAIROBI", "Jepchirchir banned 3 years for EPO."),
    (19, "SANAA", "Saudi strikes kill 11 across Yemen."),
    (20, "MOSCOW", "Russia summons Finnish envoy."),
    (21, "AIR FORCE 1", "Trump presses allies on Ukraine."),
    (22, "ALASKA", "Trump team drops Senate lawsuit."),
    (23, "CANBERRA", "Australia's jobless rate hits 4.9%."),
    (24, "BRUSSELS", "EU summons Russia envoy over Kyiv."),
    (26, "PARIS", "IEA: data-centre CO2 up 70% by 2030."),
    (27, "LONDON", "Cleverly to run for London mayor."),
    (28, "MIAMI", "148 sick on cruise ship in GI outbreak."),
    (29, "FLORIDA", "Floods close Broward, Miami schools."),
    (30, "BOGOT\u00c1", "Unions halt Colombia strike."),
    (31, "WASHINGTON", "Jeffries warns of MAGA probes."),
    (32, "HANOI", "Vietnam, Russia deepen energy ties."),
    (33, "GAZA", "Israeli forces cross ceasefire line."),
    (34, "KYIV", "Ukrainian strikes hit Russia's fuel supply."),
    (35, "WASHINGTON", "Trump frustrated by Vance."),
    (36, "NASSAU", "Cat-5 eases to Cat 4; 300 shelter."),
    (37, "NUKU'ALOFA", "Tonga drought emergency."),
]

INDEX_SOURCES = "Index sources: Reuters, AP, AFP, Al Jazeera, Euronews, Africanews, AIU, ICC, CUT, RNZ, APEC, CDC, CBS, IMD, IEA, ABS."

REGIONS_LINE = "ASIA 6  \u00b7  MIDDLE EAST 5  \u00b7  EUROPE 8  \u00b7  AFRICA 4  \u00b7  AMERICAS 8  \u00b7  OCEANIA 3  \u00b7  GLOBAL 3"

STATS = [("3", "presidents at one table"),
         ("9\u20136", "World Court vote"),
         ("$81bn", "record IPO"),
         ("$120bn", "COP31 goal cut"),
         ("109\u20130", "Arctic vote"),
         ("300,000", "evacuated")]

# map points: (lon, lat) for stories 1..37 in order (same as v2)
MAP_PTS = [
    (114.1, 22.5), (4.3, 52.1), (-74.0, 40.7), (30.7, 36.9), (30.5, 50.4),
    (36.5, 45.3), (85.8, 20.3), (12.6, 55.7), (-80.2, 25.8), (34.5, 31.5),
    (56.0, 26.5), (44.4, 33.3), (37.2, 19.6), (45.3, 2.0), (28.0, -26.2),
    (106.9, 47.9), (71.6, 34.0), (36.8, -1.3), (44.2, 15.3), (37.6, 55.8),
    (-40.0, 40.0), (-150.0, 64.0), (149.1, -35.3), (4.35, 50.85), (114.1, 22.5),
    (2.35, 48.85), (-0.1, 51.5), (-80.2, 25.8), (-80.2, 26.0), (-74.1, 4.7),
    (-77.0, 38.9), (105.8, 21.0), (34.5, 31.5), (30.5, 50.4), (-77.0, 38.9),
    (-165.4, -11.2), (-175.2, -21.1),
]

# leader-line label offsets (dx, dy in px) for crowded map dots, keyed by story no.
# v4: spread the Europe/Middle-East and US East Coast clusters radially so no
# two number badges overlap; each badge sits 14px+ from its neighbours.
# (Re-tuned after a pairwise distance check found 4 overlaps in the first
# v4 render: 4/8, 7/12, 17/32, 21/29.)
MAP_OFF = {
    1: (24, -18), 2: (-30, -24), 3: (-26, -14), 4: (-26, -6),
    5: (26, -8), 6: (30, 8), 7: (34, -18), 8: (10, -22),
    9: (24, -14), 10: (30, 20), 11: (30, -20), 12: (36, 14),
    13: (-32, 28), 14: (34, 26), 15: (18, 14), 16: (8, -26),
    17: (30, -2), 18: (-24, 26), 19: (26, 22), 20: (28, -24),
    21: (-30, 6), 24: (-32, 4), 25: (26, 14), 26: (-28, 26),
    27: (-8, -26), 28: (-24, 18), 29: (22, 16), 31: (-28, 10),
    32: (-12, 22), 33: (8, 32), 34: (-26, 22), 35: (-8, -28),
    36: (8, -10), 37: (-10, 10),
}

# ---------- rich hero illustrations (depth, shading, lighting) ----------

def ill_summit(d, x, y, w, h):
    """Shenzhen summit: warm gradient sky, lit skyline, three leaders with
    faces at a long table, flags behind, nameplates. Depth: skyline is the
    dark background, flags the midground, leaders + table the foreground."""
    # warm evening gradient: pale gold -> deep amber
    vgrad(d, x, y, w, h, (246, 214, 140), (214, 158, 74))
    # soft sun glow behind the centre (kept inside the panel)
    gx, gy = x + w // 2, y + 72
    for r, col in ((56, (250, 226, 160)), (40, (252, 232, 175)), (26, (254, 240, 195))):
        d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=col)
    # skyline silhouette (background), lit windows
    base = y + h - 62
    for bx, bw, bh in [(0, 26, 18), (30, 18, 30), (52, 22, 22), (78, 16, 34),
                       (98, 24, 17), (126, 18, 27), (148, 22, 36), (174, 18, 21),
                       (196, 24, 29), (224, 18, 19), (246, 22, 26), (272, 18, 17),
                       (294, 22, 30), (320, 18, 20), (342, 20, 24)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(122, 96, 58))
        for wy in range(base - bh + 5, base - 2, 8):
            d.rectangle([x + bx + 4, wy, x + bx + 8, wy + 3], fill=(255, 224, 130))
    # ground shadow band
    d.rectangle([x, base, x + w, base + 8], fill=(96, 72, 40))
    # flags on poles (midground)
    poles = [x + w * 0.22, x + w * 0.50, x + w * 0.78]
    flag_cols = [((178, 34, 52), (255, 255, 255), (30, 60, 130)),
                 ((222, 41, 16), (255, 220, 0), None),
                 ((255, 255, 255), (0, 57, 166), (213, 0, 50))]
    for px, cols in zip(poles, flag_cols):
        d.line([(px, y + 8), (px, base - 6)], fill=(70, 56, 34), width=3)
        fw, fh = 38, 22
        fx, fy = px + 2, y + 10
        if cols[2] is None:
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=cols[0])
            d.ellipse([fx + 5, fy + 5, fx + 12, fy + 12], fill=cols[1])
            d.ellipse([fx + 16, fy + 4, fx + 20, fy + 8], fill=cols[1])
            d.ellipse([fx + 16, fy + 12, fx + 20, fy + 16], fill=cols[1])
        elif cols[0] == (178, 34, 52):
            for i in range(7):
                d.rectangle([fx, fy + i * 3, fx + fw, fy + i * 3 + 3],
                            fill=cols[0] if i % 2 == 0 else cols[1])
            d.rectangle([fx, fy, fx + 15, fy + 11], fill=cols[2])
            d.ellipse([fx + 3, fy + 3, fx + 6, fy + 6], fill=WHITE)
            d.ellipse([fx + 9, fy + 7, fx + 12, fy + 10], fill=WHITE)
        else:
            d.rectangle([fx, fy, fx + fw, fy + 7], fill=cols[0])
            d.rectangle([fx, fy + 7, fx + fw, fy + 15], fill=cols[1])
            d.rectangle([fx, fy + 15, fx + fw, fy + 22], fill=cols[2])
    # three leaders (foreground): characteristic editorial-vector portraits.
    # Each has his own hair (Trump blond sweep, Xi neat black side-part,
    # Putin short grey-blond, receding), eyebrows, nose, lapels and tie.
    # (cx frac, skin, suit, suit_dark, hair, brow, hair_style, tie, name)
    fig = [(x + w * 0.22, (232, 182, 142), (28, 42, 84), (16, 26, 56),
            (250, 222, 132), (180, 150, 90), "sweep", (166, 30, 43), "TRUMP"),
           (x + w * 0.50, (240, 200, 160), (118, 22, 22), (80, 14, 14),
            (38, 38, 38), (30, 30, 30), "neat", (166, 30, 43), "XI"),
           (x + w * 0.78, (236, 196, 170), (52, 52, 56), (34, 34, 38),
            (222, 212, 192), (140, 130, 115), "short", (28, 58, 128), "PUTIN")]
    for cx, skin, suit, suit_d, hair, brow, style, tie, name in fig:
        cy = y + h - 78
        # soft shadow under the figure
        d.ellipse([cx - 30, y + h - 30, cx + 30, y + h - 18], fill=(150, 108, 52))
        # shoulders (structured, wider) + shirt V + lapels
        d.polygon([(cx - 36, y + h - 8), (cx + 36, y + h - 8),
                   (cx + 24, cy + 12), (cx - 24, cy + 12)], fill=suit)
        d.polygon([(cx - 7, cy + 14), (cx + 7, cy + 14), (cx, cy + 42)], fill=WHITE)
        d.polygon([(cx - 24, cy + 12), (cx - 7, cy + 14), (cx - 2, cy + 34),
                   (cx - 15, cy + 42)], fill=suit_d)
        d.polygon([(cx + 24, cy + 12), (cx + 7, cy + 14), (cx + 2, cy + 34),
                   (cx + 15, cy + 42)], fill=suit_d)
        # collar wings + tie knot + blade
        d.polygon([(cx - 8, cy + 13), (cx - 1, cy + 17), (cx - 8, cy + 21)], fill=WHITE)
        d.polygon([(cx + 8, cy + 13), (cx + 1, cy + 17), (cx + 8, cy + 21)], fill=WHITE)
        d.polygon([(cx - 4, cy + 16), (cx + 4, cy + 16), (cx + 3, cy + 23),
                   (cx - 3, cy + 23)], fill=tie)
        d.polygon([(cx - 3, cy + 23), (cx + 3, cy + 23), (cx + 2, cy + 40),
                   (cx - 2, cy + 40)], fill=tie)
        # head
        d.ellipse([cx - 18, cy - 19, cx + 18, cy + 19], fill=skin)
        # hair, characteristic per leader
        if style == "sweep":      # Trump: tall blond pompadour, swept right
            d.pieslice([cx - 18, cy - 19, cx + 18, cy - 2], 180, 360, fill=hair)
            d.ellipse([cx - 15, cy - 27, cx + 15, cy - 10], fill=hair)
            d.ellipse([cx + 4, cy - 22, cx + 20, cy - 10], fill=hair)
            d.line([(cx - 10, cy - 12), (cx - 2, cy - 14)], fill=(220, 190, 100), width=2)
        elif style == "neat":     # Xi: neat black cap, side part
            d.pieslice([cx - 18, cy - 19, cx + 18, cy - 4], 180, 360, fill=hair)
            d.ellipse([cx - 12, cy - 20, cx + 2, cy - 10], fill=hair)
            d.line([(cx - 8, cy - 17), (cx - 8, cy - 12)], fill=skin, width=2)
        else:                      # Putin: short grey-blond, receding temples
            d.pieslice([cx - 18, cy - 19, cx + 18, cy - 6], 180, 360, fill=hair)
            d.ellipse([cx - 17, cy - 10, cx - 10, cy - 1], fill=skin)
            d.ellipse([cx + 10, cy - 10, cx + 17, cy - 1], fill=skin)
        # eyebrows, eyes, nose, smile, cheek
        d.line([(cx - 12, cy - 8), (cx - 5, cy - 9)], fill=brow, width=2)
        d.line([(cx + 5, cy - 9), (cx + 12, cy - 8)], fill=brow, width=2)
        d.ellipse([cx - 9, cy - 3, cx - 5, cy + 1], fill=INK)
        d.ellipse([cx + 5, cy - 3, cx + 9, cy + 1], fill=INK)
        d.line([(cx, cy + 3), (cx, cy + 7)], fill=(200, 150, 115), width=2)
        d.arc([cx - 7, cy + 7, cx + 7, cy + 14], 20, 160, fill=INK, width=2)
        d.ellipse([cx - 13, cy + 2, cx - 9, cy + 6], fill=(245, 205, 170))
    # long table with highlight edge + gold nameplates
    d.rectangle([x + 8, y + h - 26, x + w - 8, y + h - 6], fill=(120, 70, 30))
    d.rectangle([x + 8, y + h - 26, x + w - 8, y + h - 23], fill=(190, 130, 60))
    f = font(F_SANS_B, 11)
    for cx, skin, suit, suit_d, hair, brow, style, tie, name in fig:
        tw = d.textlength(name, font=f)
        d.text((cx - tw / 2, y + h - 21), name, font=f, fill=WHITE)

def ill_icj(d, x, y, w, h):
    """The Hague: pale sky gradient, brick Peace Palace with towers, pediment
    and arched windows, steps, a flag; big gold scales of justice in the
    foreground and a red 9-6 badge. Depth: sky -> palace -> scales."""
    vgrad(d, x, y, w, h, (214, 226, 236), (238, 240, 232))
    # sun glow, top right
    d.ellipse([x + w - 64, y + 4, x + w - 8, y + 60], fill=(250, 236, 180))
    d.ellipse([x + w - 54, y + 14, x + w - 18, y + 50], fill=(252, 242, 200))
    BRICK = (172, 84, 52)
    BRICK_D = (138, 60, 36)
    CREAM = (250, 244, 228)
    bx0, bx1 = x + 26, x + w - 26
    by0, by1 = y + h - 66, y + h - 10
    # towers with pointed roofs
    for tx in (bx0 - 2, bx1 - 26):
        d.rectangle([tx, by0 - 16, tx + 26, by1], fill=BRICK_D)
        d.polygon([(tx - 3, by0 - 16), (tx + 29, by0 - 16), (tx + 13, by0 - 30)],
                  fill=NAVY2)
        d.rectangle([tx + 9, by0 + 4, tx + 17, by0 + 16], fill=CREAM)
        d.rectangle([tx + 9, by0 + 22, tx + 17, by0 + 34], fill=CREAM)
    # main body + pediment + gold roundel
    d.rectangle([bx0, by0 + 20, bx1, by1], fill=BRICK)
    d.polygon([(bx0 - 8, by0 + 22), (bx1 + 8, by0 + 22), (x + w // 2, by0 - 2)],
              fill=BRICK_D)
    d.ellipse([x + w // 2 - 9, by0 + 6, x + w // 2 + 9, by0 + 24], fill=GOLD)
    # brick courses (subtle horizontal lines)
    for by in range(by0 + 28, by1 - 4, 9):
        d.line([(bx0, by), (bx1, by)], fill=BRICK_D, width=1)
    # arched windows
    for i in range(5):
        colx = bx0 + 18 + i * ((bx1 - bx0 - 36) // 4)
        d.pieslice([colx - 8, by0 + 32, colx + 8, by0 + 48], 180, 360, fill=CREAM)
        d.rectangle([colx - 8, by0 + 40, colx + 8, by1 - 14], fill=CREAM)
        d.line([(colx, by0 + 32), (colx, by1 - 14)], fill=(200, 190, 170), width=1)
    # door + steps
    d.rectangle([x + w // 2 - 12, by1 - 22, x + w // 2 + 12, by1 - 8], fill=NAVY2)
    d.rectangle([bx0 - 6, by1 - 6, bx1 + 6, by1], fill=CREAM)
    d.rectangle([bx0 - 10, by1, bx1 + 10, by1 + 4], fill=(220, 210, 190))
    # flag on the palace roof
    fx = x + w // 2
    d.line([(fx, by0 - 2), (fx, by0 - 26)], fill=(60, 50, 30), width=2)
    d.rectangle([fx + 1, by0 - 26, fx + 22, by0 - 14], fill=(0, 90, 160))
    # scales of justice (foreground, right side, overlapping the palace)
    sx, sy = x + w - 58, y + 16
    d.line([(sx, sy), (sx, sy + 44)], fill=GOLD, width=4)
    d.line([(sx - 24, sy + 6), (sx + 24, sy + 6)], fill=GOLD, width=4)
    d.line([(sx - 24, sy + 6), (sx - 24, sy + 28)], fill=GOLD, width=2)
    d.line([(sx + 24, sy + 6), (sx + 24, sy + 28)], fill=GOLD, width=2)
    d.pieslice([sx - 32, sy + 26, sx - 16, sy + 38], 0, 180, fill=GOLD)
    d.pieslice([sx + 16, sy + 26, sx + 32, sy + 38], 0, 180, fill=GOLD)
    d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=GOLD)
    # 9-6 badge (foreground, left)
    d.ellipse([x + 12, y + 12, x + 66, y + 66], fill=RED)
    d.ellipse([x + 12, y + 12, x + 66, y + 66], outline=WHITE, width=2)
    f = font(F_SERIF_B, 21)
    d.text((x + 39, y + 39), "9\u20136", font=f, fill=WHITE, anchor="mm")

def ill_nasdaq(d, x, y, w, h):
    """Nasdaq debut: deep navy gradient, faint bar chart in the background,
    a smooth rising gold line with a glowing dot at the open and the close,
    big ANT ticker and a price strip. Depth: grid -> bars -> line -> labels."""
    vgrad(d, x, y, w, h, (10, 18, 40), (24, 38, 70))
    # faint bar chart in the background (rising volumes)
    for i, bh in enumerate((26, 34, 30, 44, 40, 52, 48, 62, 58, 74)):
        bx = x + 14 + i * ((w - 28) // 10)
        d.rectangle([bx, y + h - 44 - bh, bx + 16, y + h - 44],
                    fill=(30, 48, 84))
    # horizontal grid
    for gy in range(y + 16, y + h - 40, 22):
        d.line([(x + 10, gy), (x + w - 10, gy)], fill=(48, 66, 104), width=1)
    # smooth rising line + area fill
    pts = [(16, 96), (46, 88), (76, 80), (106, 84), (136, 70), (166, 74),
           (196, 56), (226, 60), (252, 40), (274, 44), (292, 26), (304, 16)]
    line = [(x + px, y + py) for px, py in pts]
    band = line + [(x + 304, y + h - 40), (x + 16, y + h - 40)]
    d.polygon(band, fill=(38, 54, 92))
    d.line(line, fill=GOLD_L, width=5, joint="curve")
    # glow dots at open, mid and close
    for px, py in (pts[0], pts[5], pts[-1]):
        d.ellipse([x + px - 7, y + py - 7, x + px + 7, y + py + 7],
                  fill=(255, 230, 140))
        d.ellipse([x + px - 4, y + py - 4, x + px + 4, y + py + 4],
                  fill=GOLD_L, outline=WHITE, width=1)
    # arrow head
    d.polygon([(x + 308, y + 16), (x + 292, y + 12), (x + 300, y + 30)], fill=GOLD_L)
    # ANT label + IPO DAY tag
    f = font(F_SERIF_B, 32)
    d.text((x + 14, y + 6), "ANT", font=f, fill=WHITE, anchor="la")
    f2 = font(F_SANS_B, 12)
    d.text((x + 100, y + 16), "NASDAQ \u00b7 IPO DAY", font=f2, fill=GOLD_L, anchor="la")
    # price strip
    f3 = font(F_SANS_B, 14)
    d.text((x + 12, y + h - 28), "$83.00 \u2192 $111.50", font=f3, fill=WHITE, anchor="la")
    d.text((x + w - 12, y + h - 28), "CLOSE $97", font=f3, fill=(80, 220, 130), anchor="ra")

# ---------- tier-2 illustrations (small, clear, one scene each) ----------

def ill_cop31(d, x, y, w, h):
    """Globe + thermometer + struck-through fossil fuels."""
    vgrad(d, x, y, w, h, (238, 244, 232), (224, 234, 216))
    cx, cy = x + w // 2, y + 23
    d.ellipse([cx - 19, cy - 19, cx + 19, cy + 19], fill=(70, 130, 180))
    d.ellipse([cx - 13, cy - 15, cx - 2, cy - 6], fill=GREEN)
    d.ellipse([cx + 1, cy + 1, cx + 14, cy + 13], fill=GREEN)
    d.ellipse([cx + 4, cy - 16, cx + 15, cy - 5], fill=GREEN)
    tx = x + w - 30
    d.rectangle([tx, y + 12, tx + 10, y + h - 22], fill=WHITE, outline=RED, width=2)
    d.rectangle([tx + 2, y + h - 40, tx + 8, y + h - 24], fill=RED)
    d.ellipse([tx - 3, y + h - 26, tx + 13, y + h - 10], fill=RED)
    d.line([(cx - 15, cy + 15), (cx + 15, cy - 15)], fill=RED, width=4)
    f = font(F_SANS_B, 11)
    d.text((x + w // 2, y + h - 14), "CUT FROM DRAFT", font=f, fill=RED, anchor="ma")

def ill_kyiv(d, x, y, w, h):
    """Cathedral domes + drone + explosion."""
    vgrad(d, x, y, w, h, (252, 236, 208), (244, 222, 182))
    cx = x + w // 2
    d.rectangle([cx - 36, y + h - 34, cx + 36, y + h - 12], fill=(120, 90, 60))
    d.rectangle([cx - 36, y + h - 34, cx + 36, y + h - 30], fill=(150, 115, 75))
    for dx, r in [(-23, 12), (0, 15), (23, 12)]:
        d.ellipse([cx + dx - r, y + h - 56, cx + dx + r, y + h - 30], fill=GOLD)
        d.line([(cx + dx, y + h - 60), (cx + dx, y + h - 54)], fill=GOLD, width=2)
        d.ellipse([cx + dx - 3, y + h - 52, cx + dx + 3, y + h - 46], fill=(255, 220, 120))
    dx0, dy0 = x + w - 34, y + 18
    d.ellipse([dx0 - 5, dy0 - 4, dx0 + 5, dy0 + 4], fill=INK)
    for sx, sy in [(-12, -8), (12, -8), (-12, 8), (12, 8)]:
        d.ellipse([dx0 + sx - 6, dy0 + sy - 3, dx0 + sx + 6, dy0 + sy + 3],
                  outline=INK, width=2)
    ex, ey = x + 26, y + 22
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(ex, ey), (ex + int(14 * math.cos(r)), ey + int(14 * math.sin(r)))],
               fill=ORANGE, width=3)
    d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=RED)

def ill_kerch(d, x, y, w, h):
    """Bridge over water, cracked deck, explosion, train."""
    vgrad(d, x, y, w, h, (228, 238, 244), (208, 224, 234))
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(90, 140, 180))
    for wy in range(y + h - 26, y + h, 7):
        d.line([(x + 4, wy), (x + w - 4, wy)], fill=(140, 180, 210), width=2)
    d.rectangle([x + 6, y + 20, x + w - 6, y + 28], fill=(70, 70, 78))
    d.arc([x + 20, y + 28, x + w - 20, y + 46], 180, 360, fill=(70, 70, 78), width=4)
    for px in (x + 30, x + w // 2, x + w - 30):
        d.line([(px, y + 28), (px, y + h - 30)], fill=(70, 70, 78), width=4)
    d.rectangle([x + 12, y + 10, x + 52, y + 20], fill=(40, 60, 110))
    for wx in range(x + 16, x + 50, 9):
        d.rectangle([wx, y + 13, wx + 5, y + 17], fill=(200, 220, 240))
    mx, my = x + w // 2, y + 24
    d.line([(mx - 8, my - 4), (mx + 2, my + 2), (mx - 4, my + 6), (mx + 8, my + 10)],
           fill=RED, width=3)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(mx, my - 10), (mx + int(12 * math.cos(r)), my - 10 + int(12 * math.sin(r)))],
               fill=ORANGE, width=3)
    d.ellipse([mx - 5, my - 15, mx + 5, my - 5], fill=RED)

def ill_cyclone(d, x, y, w, h):
    """Spiral storm with red eye."""
    vgrad(d, x, y, w, h, (226, 240, 244), (206, 228, 236))
    cx, cy = x + w // 2, y + 24
    for r in (5, 9, 13, 16, 18):
        d.arc([cx - r, cy - r, cx + r, cy + r], -40 + r * 3, 300 - r * 2,
              fill=(0, 90, 130) if r < 16 else (0, 60, 100), width=5)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    f = font(F_SANS_B, 11)
    d.text((x + w // 2, y + h - 11), "300,000 EVACUATED", font=f, fill=(0, 60, 100), anchor="ma")

def ill_denmark(d, x, y, w, h):
    """Greenland silhouette + Danish flag + 109-0 badge."""
    vgrad(d, x, y, w, h, (236, 242, 246), (222, 232, 240))
    d.polygon([(x + 30, y + 8), (x + 78, y + 6), (x + 108, y + 14), (x + 118, y + 28),
               (x + 100, y + 42), (x + 70, y + 46), (x + 44, y + 38), (x + 28, y + 22)],
              fill=(198, 220, 236), outline=NAVY, width=3)
    f_lab = font(F_SANS_B, 9)
    d.text((x + 72, y + 22), "GREENLAND", font=f_lab, fill=NAVY, anchor="ma")
    d.rectangle([x + 100, y + 10, x + 138, y + 32], fill=RED)
    d.rectangle([x + 112, y + 10, x + 116, y + 32], fill=WHITE)
    d.rectangle([x + 100, y + 19, x + 138, y + 23], fill=WHITE)
    d.rectangle([x + 8, y + h - 20, x + w - 8, y + h - 4], fill=NAVY)
    f = font(F_SANS_B, 11)
    d.text((x + w // 2, y + h - 12), "VOTE 109\u20130", font=f, fill=WHITE, anchor="ma")

def ill_gta(d, x, y, w, h):
    """Vice City sunset, skyline, palms, road."""
    vgrad(d, x, y, w, h, (64, 16, 88), (40, 10, 60))
    d.rectangle([x, y + 16, x + w, y + h - 26], fill=(255, 120, 60))
    d.rectangle([x, y + 24, x + w, y + h - 26], fill=(255, 170, 80))
    d.ellipse([x + w // 2 - 24, y + 2, x + w // 2 + 24, y + 50], fill=(255, 220, 120))
    d.ellipse([x + w // 2 - 24, y + 2, x + w // 2 + 24, y + 50], outline=(255, 190, 80), width=2)
    for bx, bw, bh in [(0, 18, 13), (22, 14, 20), (40, 20, 15), (64, 14, 24),
                       (82, 18, 17), (104, 16, 22), (124, 18, 14), (146, 12, 18)]:
        d.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26], fill=(30, 8, 48))
        for wy in range(y + h - 26 - bh + 4, y + h - 28, 6):
            d.rectangle([x + bx + 3, wy, x + bx + 6, wy + 3], fill=(255, 220, 120))
    for px in (x + 12, x + w - 14):
        d.line([(px, y + h - 26), (px, y + h - 46)], fill=(20, 90, 40), width=3)
        for a in (-40, -15, 15, 40):
            r = math.radians(a - 90)
            d.line([(px, y + h - 46), (px + int(12 * math.cos(r)), y + h - 46 + int(10 * math.sin(r)))],
                   fill=(20, 90, 40), width=2)
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(25, 20, 30))
    d.line([(x, y + h - 13), (x + w, y + h - 13)], fill=GOLD, width=2)

def ill_gaza(d, x, y, w, h):
    """A road reopening: checkpoint barrier lifted, road into the distance."""
    vgrad(d, x, y, w, h, (240, 232, 210), (224, 210, 180))
    # sky + distant buildings
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(190, 170, 130))
    for bx, bw, bh in [(8, 22, 14), (36, 16, 20), (58, 24, 12), (88, 18, 18),
                       (112, 22, 15), (138, 16, 20)]:
        d.rectangle([x + bx, y + h - 34 - bh, x + bx + bw, y + h - 34], fill=(140, 120, 90))
    # road (perspective): wide at bottom, narrow at horizon
    d.polygon([(x + 10, y + h), (x + w - 10, y + h),
               (x + w // 2 + 16, y + h - 34), (x + w // 2 - 16, y + h - 34)],
              fill=(90, 90, 96))
    d.line([(x + w // 2, y + h - 34), (x + w // 2, y + h)], fill=GOLD, width=2)
    # lifted barrier (diagonal, red-white) + checkpoint post
    d.line([(x + 14, y + 22), (x + w - 30, y + 6)], fill=RED, width=5)
    d.line([(x + 14, y + 22), (x + w - 30, y + 6)], fill=WHITE, width=2)
    d.rectangle([x + 10, y + 20, x + 18, y + h - 34], fill=(70, 70, 78))
    d.ellipse([x + 8, y + 14, x + 20, y + 26], fill=GOLD)
    f = font(F_SANS_B, 11)
    d.text((x + w // 2, y + h - 13), "ROAD REOPENS", font=f, fill=NAVY, anchor="ma")

def ill_apec(d, x, y, w, h):
    """A signed declaration: document, gold seal, three small flags."""
    vgrad(d, x, y, w, h, (238, 240, 244), (222, 228, 236))
    # document
    dx0, dy0, dx1, dy1 = x + 34, y + 8, x + w - 34, y + h - 12
    d.rectangle([dx0, dy0, dx1, dy1], fill=WHITE, outline=NAVY, width=2)
    d.rectangle([dx0, dy0, dx1, dy0 + 12], fill=NAVY)
    f_t = font(F_SANS_B, 9)
    d.text((x + w // 2, dy0 + 6), "SHENZHEN DECLARATION", font=f_t, fill=WHITE, anchor="mm")
    for i, ly in enumerate(range(dy0 + 20, dy1 - 14, 7)):
        lw = (dx1 - dx0 - 24) if i % 2 == 0 else (dx1 - dx0 - 44)
        d.line([(dx0 + 10, ly), (dx0 + 10 + lw, ly)], fill=(150, 150, 150), width=2)
    # gold seal
    sx, sy = x + w - 52, y + h - 26
    d.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=GOLD)
    d.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], outline=(140, 100, 20), width=2)
    d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 230, 150))
    # three small flags on the left edge
    for i, col in enumerate(((178, 34, 52), (222, 41, 16), (0, 57, 166))):
        fy = y + 12 + i * 16
        d.rectangle([x + 6, fy, x + 26, fy + 10], fill=col)

# ---------- world map (same continents as v2, dark navy panel) ----------

CONTINENTS = [
    # North America
    [(-168, 66), (-155, 58), (-140, 60), (-130, 55), (-125, 49), (-125, 40),
     (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-92, 15),
     (-86, 13), (-83, 9), (-80, 9), (-77, 8), (-79, 9), (-82, 16), (-84, 21),
     (-87, 21), (-90, 21), (-91, 19), (-90, 14), (-87, 13), (-83, 15),
     (-80, 25), (-81, 31), (-76, 35), (-75, 39), (-70, 42), (-68, 45),
     (-65, 44), (-60, 47), (-55, 47), (-59, 50), (-64, 58), (-68, 58),
     (-72, 62), (-78, 62), (-82, 66), (-86, 66), (-92, 66), (-95, 69),
     (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68), (-25, 70),
     (-20, 74), (-22, 76), (-30, 78), (-40, 80), (-55, 80), (-60, 76),
     (-68, 76), (-70, 74), (-62, 72), (-58, 68), (-58, 64)],
    # South America
    [(-79, 9), (-77, 4), (-80, 0), (-81, -6), (-81, -12), (-77, -18),
     (-72, -22), (-70, -30), (-72, -38), (-73, -46), (-70, -52), (-66, -55),
     (-65, -48), (-62, -40), (-58, -34), (-52, -32), (-48, -28), (-41, -23),
     (-39, -15), (-35, -8), (-38, -4), (-44, -2), (-50, 0), (-53, 4),
     (-58, 6), (-62, 8), (-68, 10), (-72, 11), (-77, 11), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 39), (-9, 43), (-2, 44), (-2, 48), (-4, 48),
     (-1, 50), (2, 51), (4, 53), (7, 54), (8, 57), (10, 59), (5, 60),
     (5, 62), (10, 64), (13, 66), (18, 69), (25, 71), (31, 70), (32, 68),
     (30, 64), (28, 60), (24, 59), (21, 57), (19, 55), (21, 54), (18, 54),
     (16, 54), (13, 54), (10, 54), (8, 54), (8, 57), (4, 58), (2, 57),
     (-2, 57), (-5, 56), (-6, 55), (-10, 54), (-10, 52), (-8, 52), (-6, 49),
     (-5, 48), (-2, 47), (-2, 44), (-1, 43), (-3, 43), (-9, 43), (-9, 39),
     (-10, 37), (-10, 36), (-8, 37), (-6, 36), (-2, 37), (0, 38), (3, 38),
     (3, 40), (7, 38), (8, 39), (10, 38), (12, 38), (16, 38), (16, 40),
     (18, 40), (19, 42), (19, 44), (21, 42), (23, 40), (23, 37), (26, 38),
     (26, 40), (28, 41), (29, 41), (28, 40), (27, 41), (26, 42), (28, 44),
     (29, 45), (28, 46), (25, 46), (23, 45), (21, 45), (19, 46), (16, 45),
     (14, 45), (12, 45), (10, 44), (8, 44), (8, 43), (5, 43), (3, 43),
     (0, 40), (-2, 37), (-6, 36), (-10, 36)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 25), (-13, 28), (-10, 31), (-6, 35),
     (0, 36), (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31),
     (32, 31), (34, 28), (36, 27), (38, 24), (39, 21), (41, 18), (43, 12),
     (46, 11), (51, 12), (51, 11), (48, 7), (46, 2), (42, -1), (40, -6),
     (39, -10), (38, -15), (36, -18), (35, -22), (33, -26), (32, -29),
     (30, -31), (28, -33), (25, -34), (20, -35), (18, -34), (17, -31),
     (15, -27), (14, -22), (12, -18), (13, -12), (12, -8), (9, -2), (9, 4),
     (6, 4), (3, 6), (-3, 5), (-8, 5), (-12, 8), (-15, 11), (-17, 15)],
    # Asia
    [(28, 41), (28, 45), (30, 46), (30, 50), (32, 52), (35, 55),
     (38, 58), (40, 62), (44, 66), (50, 68), (55, 69), (60, 69),
     (66, 70), (72, 72), (78, 72), (84, 73), (90, 74), (96, 76),
     (102, 77), (108, 76), (114, 74), (120, 73), (126, 72), (132, 71),
     (138, 72), (144, 71), (150, 70), (156, 69), (162, 68), (168, 66),
     (170, 66), (178, 65), (178, 64), (170, 60), (162, 58), (158, 56),
     (156, 52), (150, 59), (142, 59), (141, 52), (140, 50), (138, 46),
     (135, 43), (132, 42), (130, 42), (127, 40), (126, 38), (124, 39),
     (122, 38), (121, 34), (120, 30), (120, 26), (116, 23), (112, 21),
     (110, 20), (108, 18), (106, 16), (105, 10), (103, 8), (100, 6),
     (98, 10), (97, 15), (94, 17), (92, 21), (90, 22), (88, 22),
     (86, 20), (84, 18), (82, 16), (80, 14), (78, 9), (76, 9), (75, 13),
     (73, 19), (72, 21), (70, 22), (68, 23), (66, 25), (64, 25), (62, 25),
     (60, 25), (58, 26), (56, 27), (54, 27), (52, 28), (50, 29), (48, 30),
     (47, 30), (44, 30), (42, 31), (40, 32), (39, 32), (36, 36), (36, 36),
     (34, 36), (33, 35), (31, 36), (30, 36), (29, 38), (28, 41), (28, 41)],
    # Australia
    [(113, -22), (114, -28), (115, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -12), (132, -12), (130, -13), (127, -14), (124, -16),
     (121, -17), (118, -20), (115, -21), (113, -22)],
]

def draw_map(d, x, y, w, h):
    """Dark navy world map: tan land on deep navy, red pins, white numbers,
    leader lines for crowded clusters."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY_D)
    for gx in range(-150, 181, 30):
        px = x + int((gx + 180) / 360 * w)
        d.line([(px, y), (px, y + h)], fill=(38, 54, 92), width=1)
    for gy in range(-60, 91, 30):
        py = y + int((90 - gy) / 180 * h)
        d.line([(x, py), (x + w, py)], fill=(38, 54, 92), width=1)
    def proj(lon, lat):
        return (x + int((lon + 180) / 360 * w), y + int((90 - lat) / 180 * h))
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=(150, 128, 80))
    fnum = font(F_SANS_B, 8)
    for i, (lon, lat) in enumerate(MAP_PTS, start=1):
        px, py = proj(lon, lat)
        px = max(px, x + 8)
        px = min(px, x + w - 8)
        py = max(py, y + 8)
        py = min(py, y + h - 8)
        dx, dy = MAP_OFF.get(i, (0, 0))
        lx, ly = px + dx, py + dy
        lx = max(lx, x + 8)
        lx = min(lx, x + w - 8)
        ly = max(ly, y + 8)
        ly = min(ly, y + h - 8)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED, outline=WHITE, width=1)
        if dx or dy:
            d.line([(px, py), (lx, ly)], fill=(150, 150, 145), width=1)
        d.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=RED, outline=WHITE, width=1)
        d.text((lx, ly), str(i), font=fnum, fill=WHITE, anchor="mm")
    return y + h

# ---------- page assembly (magazine layout) ----------

def main():
    img = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(img)
    M = 24                      # side margin
    CW = W - 2 * M              # content width = 976

    # outer double rule
    d.rectangle([8, 8, W - 9, H - 9], outline=GOLD, width=2)
    d.rectangle([13, 13, W - 14, H - 14], outline=NAVY, width=1)

    # ---- masthead ----
    y = 22
    f_mast = font(F_SANS_B, 20)
    d.text((M, y), "THE WORLD IN ONE DAY", font=f_mast, fill=RED, anchor="la")
    f_mast_r = font(F_SANS_B, 13)
    d.text((W - M, y + 3), "37 STORIES  \u00b7  SEVEN REGIONS  \u00b7  ONE DAY",
           font=f_mast_r, fill=NAVY, anchor="ra")
    y += 26
    gold_rule(d, M, W - M, y)
    y += 9

    # ---- date headline (the giant anchor) ----
    f_date = font(F_SERIF_B, 56)
    d.text((W // 2, y), "Thursday 19 November 2026", font=f_date, fill=NAVY, anchor="ma")
    y += 62
    f_sub = font(F_SERIF_I, 17)
    d.text((W // 2, y),
           "Trump, Xi and Putin share one table  \u00b7  The World Court finds genocide in Myanmar  \u00b7  Anthropic's record IPO debuts",
           font=f_sub, fill=RED, anchor="ma")
    y += 21
    # region line (small caps, no boxes)
    f_reg = font(F_SANS_B, 11)
    d.text((W // 2, y), REGIONS_LINE, font=f_reg, fill=GREY, anchor="ma")
    y += 16
    gold_rule(d, M, W - M, y)
    y += 7

    # ---- slim stat line (one line, no boxes: numbers + labels inline) ----
    f_stat = font(F_SERIF_B, 20)
    f_stat_l = font(F_SANS, 11)
    # true width: sum of each number (stat font) + label (label font) + separators
    sep = "  \u00b7  "
    sep_w = d.textlength(sep, font=f_stat_l)
    seg_w = []
    for num, label in STATS:
        seg_w.append(d.textlength(num, font=f_stat) + d.textlength(" " + label, font=f_stat_l))
    total_w = sum(seg_w) + sep_w * (len(STATS) - 1)
    cur = (W - total_w) // 2
    for i, (num, label) in enumerate(STATS):
        nw = d.textlength(num, font=f_stat)
        lw = d.textlength(" " + label, font=f_stat_l)
        d.text((cur, y + 2), num, font=f_stat, fill=NAVY, anchor="la")
        d.text((cur + nw, y + 6), " " + label, font=f_stat_l, fill=GREY, anchor="la")
        cur += nw + lw
        if i < len(STATS) - 1:
            d.text((cur, y + 6), sep, font=f_stat_l, fill=GOLD, anchor="la")
            cur += sep_w
    y += 24
    hline(d, M, W - M, y, fill=(210, 200, 175), w=1)
    y += 6

    # ---- hero row: 3 UNEQUAL feature panels (summit widest) ----
    hero_h = 256
    hero_gap = 10
    hero_ws = [380, 288, 288]   # summit, ICJ, Anthropic
    f_kick = font(F_SANS_B, 11)
    f_head = font(F_SERIF_B, 21)
    f_head_s = font(F_SERIF_B, 19)
    f_deck = font(F_SANS, 12)
    f_src = font(F_SANS_B, 10)
    ill_fns = [ill_summit, ill_icj, ill_nasdaq]
    hx = M
    for i, (kick, head, deck, src) in enumerate(HEROES):
        hw = hero_ws[i]
        # panel: paper fill, thin outline only
        d.rectangle([hx, y, hx + hw, y + hero_h], fill=PAPER2, outline=NAVY, width=1)
        ill_h = 138
        ill_fns[i](d, hx + 1, y + 1, hw - 2, ill_h)
        ty = y + ill_h + 8
        kicker(d, hx + 10, ty, kick, f_kick)
        ty += 16
        hf = f_head if i == 0 else f_head_s
        lines = wrap(d, head, hf, hw - 20)
        ty = para(d, hx + 10, ty, lines[:2], hf, fill=NAVY, leading=23 if i == 0 else 22)
        lines = wrap(d, deck, f_deck, hw - 20)
        ty = para(d, hx + 10, ty + 2, lines[:2], f_deck, fill=INK, leading=15)
        d.text((hx + 10, y + hero_h - 14), "Source: " + src, font=f_src, fill=GREY, anchor="la")
        hx += hw + hero_gap
    y += hero_h + 2

    # ---- second tier: 2 rows x 4 medium features ----
    tier_h = 134
    tier_gap = 10
    tier_w = (CW - 3 * tier_gap) // 4
    f_tkick = font(F_SANS_B, 9)
    f_thead = font(F_SERIF_B, 14)
    f_tdeck = font(F_SANS, 10)
    f_tsrc = font(F_SANS_B, 8)
    tier_ill = [ill_cop31, ill_kyiv, ill_kerch, ill_cyclone,
                ill_denmark, ill_gta, ill_gaza, ill_apec]
    for row in range(2):
        for col in range(4):
            i = row * 4 + col
            num, kick, head, deck, src = TIER2[i]
            tx0 = M + col * (tier_w + tier_gap)
            ty0 = y + row * (tier_h + 8)
            # panel: paper fill, hairline outline (quiet, not a grid cell)
            d.rectangle([tx0, ty0, tx0 + tier_w, ty0 + tier_h], fill=PAPER2,
                        outline=(200, 190, 160), width=1)
            ill_h = 56
            tier_ill[i](d, tx0 + 1, ty0 + 1, tier_w - 2, ill_h)
            ty = ty0 + ill_h + 5
            kicker(d, tx0 + 7, ty, f"{num} \u00b7 {kick}", f_tkick)
            ty += 13
            lines = wrap(d, head, f_thead, tier_w - 14)
            ty = para(d, tx0 + 7, ty, lines[:2], f_thead, fill=NAVY, leading=16)
            lines = wrap(d, deck, f_tdeck, tier_w - 14)
            ty = para(d, tx0 + 7, ty + 1, lines[:1], f_tdeck, fill=INK, leading=12)
            d.text((tx0 + 7, ty0 + tier_h - 11), "Source: " + src, font=f_tsrc,
                   fill=GREY, anchor="la")
    y += 2 * tier_h + 6 + 2

    # ---- bottom band: dark map feature + quiet index ----
    sec_top = y
    map_w = 344
    idx_x = M + map_w + 12
    idx_w = W - M - idx_x
    sec_h = 218
    # map panel (dark navy feature)
    d.rectangle([M, sec_top, M + map_w, sec_top + sec_h], fill=NAVY_D, outline=NAVY, width=2)
    f_map_t = font(F_SANS_B, 13)
    d.text((M + 10, sec_top + 8), "WHERE IT HAPPENED", font=f_map_t, fill=WHITE, anchor="la")
    f_map_s = font(F_SANS, 10)
    d.text((M + map_w - 10, sec_top + 9), "numbers = stories 1\u201337",
           font=f_map_s, fill=(190, 200, 220), anchor="ra")
    draw_map(d, M + 6, sec_top + 30, map_w - 12, sec_h - 56)
    f_map_c = font(F_SANS, 10)
    d.text((M + map_w // 2, sec_top + sec_h - 22),
           "Every dot is a story on this page.",
           font=f_map_c, fill=(190, 200, 220), anchor="ma")
    # index header
    f_idx_t = font(F_SANS_B, 13)
    d.text((idx_x, sec_top + 8), "ALSO ON THURSDAY 19 NOVEMBER", font=f_idx_t, fill=NAVY, anchor="la")
    f_idx_s = font(F_SANS, 10)
    d.text((idx_x + idx_w, sec_top + 9), "26 more stories", font=f_idx_s, fill=GREY, anchor="ra")
    hline(d, idx_x, idx_x + idx_w, sec_top + 28, fill=GOLD, w=2)
    # index: 26 stories, 2 columns, one line each (11pt, roomier than v3)
    f_num = font(F_SANS_B, 11)
    f_list = font(F_SANS, 11)
    col_w = idx_w // 2
    per_col = 13
    overflow = []
    for idx, (n, place, head) in enumerate(INDEX):
        col = 0 if idx < per_col else 1
        row = idx % per_col
        lx = idx_x + col * col_w
        ly = sec_top + 34 + row * 14
        d.rectangle([lx, ly, lx + 22, ly + 14], fill=RED)
        d.text((lx + 11, ly + 7), str(n), font=f_num, fill=WHITE, anchor="mm")
        d.text((lx + 26, ly), place + ": ", font=f_num, fill=NAVY, anchor="la")
        pw = d.textlength(place + ": ", font=f_num)
        d.text((lx + 26 + pw, ly), head, font=f_list, fill=INK, anchor="la")
        total = 26 + pw + d.textlength(head, font=f_list)
        if total > col_w - 2:
            overflow.append((n, place, round(total), col_w))
    y = sec_top + sec_h + 4
    f_src_l = font(F_SANS, 10)
    d.text((M, y), INDEX_SOURCES, font=f_src_l, fill=GREY, anchor="la")
    y += 12

    # ---- DATE CHECK footer ----
    f_foot_t = font(F_SANS_B, 11)
    f_foot = font(F_SANS, 10)
    d.rectangle([M, y, W - M, y + 32], outline=RED, width=2)
    d.text((M + 8, y + 4), "DATE CHECK \u2014 left out because they were other days' news:",
           font=f_foot_t, fill=RED, anchor="la")
    d.text((M + 8, y + 19),
           "18 NOV: EU's \u20ac45bn Ukraine loan \u00b7 Iran strikes on Kuwait & Bahrain \u00b7 Nvidia results \u00b7 Jeffries for speaker \u00b7 Russian bombers in Vietnam.  20 NOV: COP31 close \u00b7 Akvan landfall \u00b7 UK\u2013EU deal.",
           font=f_foot, fill=INK, anchor="la")
    y += 36

    # ---- bottom line (one line) ----
    f_bot = font(F_SANS, 9)
    d.text((M, y),
           "Every story here happened, or was first reported, on Thursday 19 November 2026. Disputed claims are attributed, not stated as fact. All pictures and the map are drawn in code.",
           font=f_bot, fill=GREY, anchor="la")

    img.save(OUT, optimize=True)
    print(f"saved {OUT} {img.size} final_y={y}")
    if overflow:
        print("INDEX OVERFLOW (story, place, width, col_w):")
        for o in overflow:
            print("  ", o)
    else:
        print("index: no overflow")

if __name__ == "__main__":
    main()
