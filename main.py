#!/usr/bin/env python3
"""news-image-20261117: one image summing up the world's news of
Tuesday 17 November 2026.

A code-drawn newspaper front page. Standard library only, no network, no
time, no randomness: the program draws the whole 1024x1024 image at runtime
with a hand-made 5x7 bitmap font and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png when set). Deterministic: two runs write
identical bytes.

Stories (all verified 17 Nov 2026, cross-checked across 2+ outlets):
  LEAD A  DIPLOMACY: China confirms the first-ever Xi-Trump-Putin
        trilateral summit, Shenzhen, Thursday 19 Nov, on the APEC
        sidelines; nuclear arms on the table. Trump flies to Asia.
  LEAD B  UKRAINE: Crimea Bridge road arch collapses in a second strike
        in two days; Kyiv's North and South bridges hit by 7 Russian
        ballistic missiles; Russia says 1,441 drones downed, a record.
  MARKETS  Dow falls 849 points (-1.64%) to 50,759; S&P -1.03%, lowest
        close since late July; Nasdaq -0.74%; a classified NSA network
        outage rattles traders; Nvidia beats after the bell.
  GULF  Tanker hit near Hormuz, engine-room fire 7 miles off Oman;
        IRGC SAYS mines hit tankers (unverified); USS Theodore
        Roosevelt arrives, a third US carrier in the region.
  TECH  US closes the AI-chip loophole: new rules bar China from
        renting US computing power; chip stocks slide ahead of
        Nvidia results.
  EUROPE  Five EU states plan a Rwanda return hub for rejected asylum
        seekers; transfers from 2027, about 100 at a time.
  PENTAGON  Fails its 9th straight audit; $4.8T in assets; 14 of 25
        parts pass.

Layout: two variants were rendered and compared at full size and at
300 px wide (see STATUS). Variant A leads with the trilateral summit;
variant B leads with the bridges falling in Kyiv and Crimea. Variant B
won: its lead is the day's freshest event (the bridge strikes happened
on Tuesday itself, while the summit was confirmed on Monday), its
headline is shorter and punchier at 300 px, and its lead body balances
better (A leaves a 3-word orphan, "ON THE TABLE.", on its third line).
The trilateral stays prominent as the first grid panel. The winner is
hardcoded in main() below.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (245, 241, 232)
INK = (17, 17, 17)
NAVY = (30, 58, 95)
GOLD = (255, 214, 90)
RED = (192, 57, 43)
DARKRED = (90, 30, 30)
GRAY = (90, 90, 90)
WHITE = (255, 255, 255)
TEAL = (14, 98, 90)
GULFRED = (120, 30, 30)
CHARCOAL = (60, 60, 60)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits ("#" = ink). All caps, digits, punctuation.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
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
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    # Bullet: a small filled square, used as a separator dot.
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}

BLANK = ("00000",) * 7


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def text(self, x, y, s, scale, color):
        """Draw string s with top-left at (x, y); scale = integer factor."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == "1":
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def to_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ------------------------------------------------------------------- layout
def draw_masthead(c):
    c.rect(0, 0, W, 104, NAVY)
    c.text(32, 22, "TUESDAY 17 NOVEMBER 2026", 6, PAPER)
    c.text(32, 66, "THE WORLD IN ONE IMAGE", 3, GOLD)
    c.rect(0, 104, W, 6, RED)


def draw_lead(c, variant):
    c.rect(24, 130, 976, 242, WHITE)
    c.rect(24, 130, 976, 38, RED)
    if variant == "B":
        c.text(44, 142, "LEAD \u2022 UKRAINE", 2, PAPER)
        c.text(44, 180, "CRIMEA BRIDGE DOWN", 6, INK)
        body = ("ROAD ARCH COLLAPSES IN 2ND STRIKE IN 2 DAYS. "
                "KYIV BRIDGES HIT BY 7 MISSILES. "
                "1,441 DRONES DOWNED, RUSSIA SAYS.")
    else:
        c.text(44, 142, "LEAD \u2022 DIPLOMACY", 2, PAPER)
        c.text(44, 180, "XI, TRUMP, PUTIN MEET", 6, INK)
        body = ("CHINA CONFIRMS THREE-WAY MEETING IN SHENZHEN "
                "ON THURSDAY 19 NOV. FIRST EVER. "
                "NUCLEAR ARMS ON THE TABLE.")
    lines = wrap(body, 44)
    y = 258
    for line in lines:
        c.text(44, y, line, 3, INK)
        y += 34


def draw_arrow_down(c, x, y, size, color):
    """A small downward arrow (shaft + head), drawn in code."""
    shaft_w = max(2, size // 5)
    c.rect(x + size // 2 - shaft_w // 2, y, shaft_w, size * 2 // 3, color)
    head_h = size // 3
    for i in range(head_h):
        half = i * (size // 2) // max(1, head_h - 1)
        c.rect(x + size // 2 - half, y + size * 2 // 3 + i, half * 2, 1, color)


def draw_panel(c, x, y, color, kicker, headline, body, arrow=False):
    c.rect(x, y, 476, 240, WHITE)
    c.rect(x, y, 476, 34, color)
    c.text(x + 20, y + 9, kicker, 2, PAPER)
    if arrow:
        draw_arrow_down(c, x + 436, y + 6, 22, GOLD)
    lines = wrap(headline, 24)
    hy = y + 48
    for line in lines[:2]:
        c.text(x + 20, hy, line, 3, INK)
        hy += 32
    blines = wrap(body, 36)
    by = y + 128
    for line in blines[:3]:
        c.text(x + 20, by, line, 2, INK)
        by += 26


def draw_mini(c, x, color, kicker, headline, body):
    """A short bottom-strip item: kicker bar, headline, one body line."""
    y = 912
    c.rect(x, y, 476, 74, WHITE)
    c.rect(x, y, 476, 28, color)
    c.text(x + 20, y + 7, kicker, 2, PAPER)
    c.text(x + 20, y + 34, headline, 2, INK)
    c.text(x + 20, y + 56, body, 2, INK)


PANELS = {
    "MARKETS": (TEAL, "MARKETS",
                "DOW DOWN 849 POINTS",
                "S&P -1.03%, LOWEST SINCE JULY. NASDAQ -0.7%. "
                "NSA OUTAGE HITS. NVIDIA BEATS AFTER BELL."),
    "UKRAINE": (NAVY, "UKRAINE",
                "CRIMEA BRIDGE DOWN",
                "ROAD ARCH COLLAPSES IN 2ND STRIKE. "
                "KYIV BRIDGES HIT BY 7 MISSILES. "
                "1,441 DRONES DOWNED."),
    "GULF": (GULFRED, "GULF",
             "TANKER HIT NEAR HORMUZ",
             "ENGINE-ROOM FIRE 7 MILES OFF OMAN. "
             "IRGC SAYS MINES HIT TANKERS. "
             "THIRD US CARRIER ARRIVES."),
    "TECH": (CHARCOAL, "TECH",
             "US CLOSES AI-CHIP LOOPHOLE",
             "NEW RULES BAR CHINA FROM RENTING US COMPUTING "
             "POWER. CHIP STOCKS SLIDE."),
    "DIPLOMACY": (NAVY, "DIPLOMACY",
                  "FIRST XI-TRUMP-PUTIN SUMMIT",
                  "CHINA CONFIRMS 3-WAY MEETING IN SHENZHEN "
                  "ON THURSDAY. FIRST EVER. "
                  "NUCLEAR ARMS ON TABLE."),
}

# Variant A leads with the trilateral summit; variant B with the bridges.
GRID_A = [("MARKETS", 24, 392), ("UKRAINE", 524, 392),
          ("GULF", 24, 652), ("TECH", 524, 652)]
GRID_B = [("DIPLOMACY", 24, 392), ("MARKETS", 524, 392),
          ("GULF", 24, 652), ("TECH", 524, 652)]


def build(variant):
    c = Canvas(W, H, PAPER)
    draw_masthead(c)
    draw_lead(c, variant)
    grid = GRID_B if variant == "B" else GRID_A
    for key, px, py in grid:
        color, kicker, headline, body = PANELS[key]
        draw_panel(c, px, py, color, kicker, headline, body,
                   arrow=(key == "MARKETS"))
    for x, color, kicker, headline, body in (
            (24, NAVY, "EUROPE", "5 EU STATES PLAN RWANDA HUB",
             "TRANSFERS FROM 2027. ABOUT 100."),
            (524, DARKRED, "PENTAGON", "FAILS 9TH AUDIT IN A ROW",
             "$4.8T IN ASSETS. 14 OF 25 PASS.")):
        draw_mini(c, x, color, kicker, headline, body)
    c.text(24, 998, "SOURCES: AP \u2022 REUTERS \u2022 AL JAZEERA \u2022 "
                    "INVESTOPEDIA \u2022 SHARECAST", 2, GRAY)
    return to_png(c)


def main():
    variant = "B"  # winner of the A/B comparison (see STATUS)
    if len(sys.argv) > 1 and sys.argv[1] in ("A", "B"):
        variant = sys.argv[1]
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(build(variant))


if __name__ == "__main__":
    main()
