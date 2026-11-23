#!/usr/bin/env python3
"""Render the 23 Nov 2026 make.fun newspaper front page (1024x1024).

Fresh renderer for the news-image-20261123 entry. Layout mirrors the
22 Nov newspaper that scored 0.981: cream paper, huge date masthead,
banner photo + cover headline, 8 photo feature tiles, 16-item ALSO ON
list, sage world map + DATE CHECK box.

Revision (Xie, 23 Nov 12:27 WIB): the world map is now a real visible
200x99 sage map with red dots on the story locations (the first build's
map was invisible — its threshold dropped the light-grey borders), and
stories 9-12 (MSCI, South Korea, India, Taiwan) are promoted with a
52x40 photo thumb each. Space was freed by trimming the banner and the
feature-tile photos.
"""
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(BASE, "photos")

W, H = 1024, 1024
CREAM = (246, 241, 231)
INK = (17, 17, 17)
RED = (193, 39, 45)
DARKRED = (150, 25, 30)
GREY = (90, 86, 80)
SAGE = (122, 139, 111)

F_DISPLAY = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size, fallback):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(fallback, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def cover_crop(im, tw, th, focus_y=0.5):
    """Crop image to fill tw x th, keeping the vertical focus point."""
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - tw) // 2
    cy = int(nh * focus_y)
    y0 = min(max(cy - th // 2, 0), nh - th)
    return im.crop((x0, y0, x0 + tw, y0 + th))


DOTS = [  # (lat, lon) of the main story locations, equirectangular map
    (26.68, -80.03),   # Mar-a-Lago, Florida
    (50.85, 4.35),     # Brussels
    (37.57, 126.98),   # Seoul
    (28.6, 77.2),      # Delhi
    (36.9, 30.7),      # Antalya (COP31)
    (25.03, 121.56),   # Taipei
    (-6.2, 106.85),    # Jakarta
    (-15.5, 167.0),    # Vanuatu
]


def sage_map(w, h):
    """Recolour the blank world map to sage green on transparent, with red
    dots marking the main story locations. NOTE: the source map's borders
    are light grey (~160-200), so the threshold must be 235 — the old
    threshold of 160 rendered nothing at all."""
    from PIL import ImageFilter
    m = Image.open(os.path.join(PHOTOS, "worldmap.png")).convert("L")
    m = m.resize((w, h), Image.LANCZOS)
    mask = m.point(lambda v: 255 if v < 235 else 0)
    mask = mask.filter(ImageFilter.MaxFilter(3))  # thicken hairlines
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sage = Image.new("RGBA", (w, h), SAGE + (255,))
    out.paste(sage, (0, 0), mask)
    dd = ImageDraw.Draw(out)
    for lat, lon in DOTS:
        x = (lon + 180) / 360 * w
        y = (90 - lat) / 180 * h
        dd.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 255))
        dd.ellipse([x - 3, y - 3, x + 3, y + 3], fill=RED + (255,))
    return out


# ---------------------------------------------------------------- stories
COVER = {
    "headline": "TRUMP WARNS IRAN: REBUILD AND WE STRIKE AGAIN",
    "deck": [
        "At Mar-a-Lago, the president backs Israeli action on Iran's missiles, pushes Gaza",
        "ceasefire phase two \u2014 and renews his call for a Netanyahu pardon.",
    ],
    "caption": "Trump and Netanyahu at the White House in February \u2014 they met again on Monday at Mar-a-Lago, Florida. Photo: Dan Scavino",
}

TILES = [
    {"label": "KOSPI", "loc": "1 \u2022 SEOUL \u2022 ASIA", "photo": "kospi.jpg",
     "head": "Kospi tumbles 3.74% on AI-bubble fears",
     "desc": "Samsung -3.4%, SK Hynix -2.8% as Asian stocks slide on Monday.",
     "credit": "Photo: USAGI_POST (CC0)"},
    {"label": "BITCOIN", "loc": "2 \u2022 GLOBAL", "photo": "bitcoin.jpg",
     "head": "Bitcoin bounces back above $60,000",
     "desc": "Near $61,000, a second day of gains after Saturday's two-year low near $55,100.",
     "credit": "Photo: Satheesh Sankaran"},
    {"label": "NATO", "loc": "3 \u2022 BRUSSELS \u2022 EUROPE", "photo": "nato.jpg",
     "head": "NATO meets on Poland missile incursion",
     "desc": "Allies gather after prosecutors confirmed all three objects were Russian Kh-101 missiles.",
     "credit": "Photo: Romaine (CC0)"},
    {"label": "NHS TRIAL", "loc": "4 \u2022 LONDON \u2022 EUROPE", "photo": "nhs.jpg",
     "head": "NHS launches biggest AI breast-cancer trial",
     "desc": "Some 700,000 women at 30 UK sites in the EDITH trial, the largest of its kind.",
     "credit": "Photo: National Cancer Institute"},
    {"label": "NEPAL\u2013INDIA", "loc": "5 \u2022 NEW DELHI \u2022 ASIA", "photo": "modi.jpg",
     "head": "Nepal's PM Balen Shah meets Modi",
     "desc": "Delegation talks and a joint press conference; a new Ayodhya\u2013Janakpur train flagged off.",
     "credit": "Photo: Narendra Modi (CC BY 2.0)", "focus": 0.32},
    {"label": "VANUATU QUAKE", "loc": "6 \u2022 PACIFIC", "photo": "vanuatu.jpg",
     "head": "M6.5 quake shakes deep under Vanuatu",
     "desc": "The 02:40 UTC tremor struck some 600 km down; no damage reported.",
     "credit": "Photo: Wikimedia Commons"},
    {"label": "OIL", "loc": "7 \u2022 GLOBAL", "photo": "oil.jpg",
     "head": "Oil falls as AI sell-off spreads",
     "desc": "Brent $92.29, WTI $83.26; attacks on Gulf shipping limit the losses.",
     "credit": "Photo: DeltaSquad833"},
    {"label": "FIFA VOTE", "loc": "8 \u2022 ZURICH \u2022 SPORT", "photo": "fifa.jpg",
     "head": "FIFA votes today on UK 2035 World Cup",
     "desc": "The unopposed \u2018All Together\u2019 bid: 48 teams, 104 matches, 19 venues.",
     "credit": "Photo: Lewis Clarke"},
]

ALSO = [
    ("MSCI", "MSCI discussed avoiding an Indonesia downgrade with President Prabowo. (Reuters)"),
    ("SOUTH KOREA", "Finance minister sees solid growth next year, but flags chip volatility. (Reuters)"),
    ("INDIA", "Shares open higher on record $13bn November foreign inflows; rupee 92.67. (Reuters)"),
    ("TAIWAN", "Short-selling ban takes effect today after the Taiex fell 17.5% in a week. (FSC)"),
    ("SHURI CASTLE", "Main hall opens in Okinawa, seven years after the 2019 fire. (AP)"),
    ("FLASH PMI", "India and US flash PMI data due Monday as markets gauge the slowdown. (S&P Global)"),
    ("COP31", "A day after COP31 collapsed in Antalya, the UN chief says he is \u2018deeply disappointed\u2019. (Reuters)"),
    ("MADURO", "Trump says he spoke to Venezuela\u2019s Maduro \u2018pretty recently\u2019, but the talks produced little. (AFP)"),
    ("WORLD CUP 2031", "FIFA\u2019s Congress is also set to approve the US\u2013Mexico\u2013Costa Rica\u2013Jamaica bid for 2031. (BBC)"),
    ("DRUG DOCK", "Trump says the US hit a shore facility where drug boats \u2018load up\u2019. (AFP)"),
    ("DRUG BOATS", "Another US boat strike in the eastern Pacific kills two; campaign toll at least 107. (AFP)"),
    ("SELANGOR", "Flood evacuees fall to 1,594 as waters recede; high tides expected through Friday. (Media Selangor)"),
    ("IRAN PROTESTS", "Central bank chief quits as the rial hits a record low and the biggest protests in three years erupt. (AP)"),
    ("IOWA", "The Army\u2019s planned Monday blast of 5 tons of unstable explosive stays halted by a judge. (CNN)"),
    ("DYMER", "Death toll rises to nine as rescuers race on Monday to find residents under the rubble. (Reuters)"),
    ("ODESA", "All schools switch to remote learning from today through Friday after strikes wreck the grid. (Ukrenergo)"),
]

TICKER = [("EUROPE", 5, (46, 90, 136)), ("GLOBAL", 3, (102, 102, 102)),
          ("MIDDLE EAST", 3, (139, 90, 43)), ("AMERICAS", 4, (193, 39, 45)),
          ("ASIA", 8, (46, 125, 50)), ("SPORT", 1, (230, 81, 0)),
          ("OCEANIA", 1, (0, 131, 143))]


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    MX = 20                      # side margin
    CW = W - 2 * MX              # content width

    f_kick = font(F_SANS_B, 13, F_SANS_B)
    f_mast = font(F_DISPLAY, 56, F_SERIF_B)
    f_deck = font(F_SERIF_I, 17, F_SERIF)
    f_tick = font(F_SANS_B, 11, F_SANS_B)
    f_cap = font(F_SERIF_I, 12, F_SERIF)
    f_cover = font(F_SERIF_B, 36, F_SERIF_B)
    f_cdeck = font(F_SERIF, 16, F_SERIF)
    f_lab = font(F_SANS_B, 10, F_SANS_B)
    f_loc = font(F_SANS_B, 9, F_SANS_B)
    f_head = font(F_SERIF_B, 14, F_SERIF_B)
    f_desc = font(F_SERIF, 12, F_SERIF)
    f_cred = font(F_SANS, 8, F_SANS)
    f_also_h = font(F_SANS_B, 13, F_SANS_B)
    f_num = font(F_SERIF_B, 13, F_SERIF_B)
    f_key = font(F_SANS_B, 11, F_SANS_B)
    f_item = font(F_SERIF, 11, F_SERIF)
    f_date = font(F_SANS_B, 13, F_SANS_B)
    f_date2 = font(F_SERIF, 13, F_SERIF)
    f_foot = font(F_SANS, 9, F_SANS)

    y = 10
    # kicker
    d.text((W // 2, y), "T H E   W O R L D   I N   O N E   D A Y",
           font=f_kick, fill=DARKRED, anchor="ma")
    y += 22
    # masthead
    d.text((W // 2, y), "Monday 23 November 2026", font=f_mast, fill=INK, anchor="ma")
    y += 66
    # deck
    d.text((W // 2, y), "Trump meets Netanyahu at Mar-a-Lago  \u2022  Kospi slides on AI fears  \u2022  Bitcoin bounces back above $60,000",
           font=f_deck, fill=INK, anchor="ma")
    y += 22
    # ticker
    parts, widths = [], []
    for name, n, col in TICKER:
        parts.append((name, n, col))
        widths.append(d.textlength(f"{name} {n}", font=f_tick) + 26)
    total = sum(widths) + 18 * (len(parts) - 1)
    x = (W - total) // 2
    for (name, n, col), wdt in zip(parts, widths):
        d.rectangle([x, y + 1, x + 9, y + 10], fill=col)
        d.text((x + 13, y), f"{name} {n}", font=f_tick, fill=INK)
        x += wdt + 18
    y += 18
    d.line([(MX, y), (W - MX, y)], fill=INK, width=2)
    y += 6

    # banner photo
    banner = Image.open(os.path.join(PHOTOS, "banner.jpg")).convert("RGB")
    banner = cover_crop(banner, CW, 66, focus_y=0.20)
    img.paste(banner, (MX, y))
    y += 66 + 4
    d.text((MX, y), COVER["caption"], font=f_cap, fill=INK)
    y += 15
    # cover headline + deck
    d.text((W // 2, y), COVER["headline"], font=f_cover, fill=INK, anchor="ma")
    y += 42
    for line in COVER["deck"]:
        d.text((W // 2, y), line, font=f_cdeck, fill=INK, anchor="ma")
        y += 19
    y += 4
    d.line([(MX, y), (W - MX, y)], fill=RED, width=2)
    y += 8

    # feature tiles 4 x 2
    gap = 12
    tw = (CW - 3 * gap) // 4
    th_photo = 44
    row_h = 17 + th_photo + 3 + 13 + 34 + 30 + 10
    for row in range(2):
        row_y = y + row * (row_h + 4)
        for col in range(4):
            t = TILES[row * 4 + col]
            tx = MX + col * (tw + gap)
            d.rectangle([tx, row_y, tx + tw, row_y + 17], fill=RED)
            d.text((tx + 5, row_y + 3), t["label"], font=f_lab, fill=(255, 255, 255))
            ph = Image.open(os.path.join(PHOTOS, t["photo"])).convert("RGB")
            ph = cover_crop(ph, tw, th_photo, focus_y=t.get("focus", 0.45))
            img.paste(ph, (tx, row_y + 17))
            ty = row_y + 17 + th_photo + 3
            d.text((tx, ty), t["loc"], font=f_loc, fill=DARKRED)
            ty += 13
            for line in wrap(d, t["head"], f_head, tw)[:2]:
                d.text((tx, ty), line, font=f_head, fill=INK)
                ty += 17
            for line in wrap(d, t["desc"], f_desc, tw)[:2]:
                d.text((tx, ty), line, font=f_desc, fill=INK)
                ty += 15
            d.text((tx, ty + 1), t["credit"], font=f_cred, fill=GREY)
    y += 2 * (row_h + 4)

    # ALSO ON header
    d.text((MX, y), "ALSO ON MONDAY 23 NOVEMBER 2026  \u2022  16 MORE STORIES",
           font=f_also_h, fill=DARKRED)
    y += 14
    d.line([(MX, y), (W - MX, y)], fill=INK, width=1)
    y += 6

    # ALSO ON items: 2 columns x 8 rows. Rows 0-1 carry a 52x40 photo thumb
    # for the four promoted stories (MSCI, South Korea, India, Taiwan);
    # the other rows are text-only, as before.
    PROMO = {0: ("msci.jpg", 0.45), 1: ("korea.jpg", 0.5),
             2: ("india.jpg", 0.4), 3: ("taiwan.jpg", 0.5)}
    col_w = (CW - 24) // 2
    row_heights = [40, 40, 25, 25, 25, 25, 25, 25]
    row_y = [y]
    for rh in row_heights:
        row_y.append(row_y[-1] + rh)
    for i, (key, text) in enumerate(ALSO):
        col = i % 2
        r = i // 2
        ix = MX + col * (col_w + 24)
        iy = row_y[r]
        num = f"{9 + i}"
        if i in PROMO:
            ph_file, foc = PROMO[i]
            ph = Image.open(os.path.join(PHOTOS, ph_file)).convert("RGB")
            ph = cover_crop(ph, 52, 40, focus_y=foc)
            img.paste(ph, (ix, iy))
            tx = ix + 58
            tw2 = col_w - 58
            d.text((tx, iy), num, font=f_num, fill=DARKRED)
            nx = tx + d.textlength(num + " ", font=f_num)
            d.text((nx, iy + 1), key, font=f_key, fill=INK)
            kx = nx + d.textlength(key + " ", font=f_key)
            first = wrap(d, text, f_item, tw2 - (kx - tx))
            d.text((kx, iy + 1), first[0] if first else "", font=f_item, fill=INK)
            if len(first) > 1:
                d.text((tx, iy + 13), first[1], font=f_item, fill=INK)
            if len(first) > 2:
                d.text((tx, iy + 25), first[2], font=f_item, fill=INK)
        else:
            d.text((ix, iy), num, font=f_num, fill=DARKRED)
            nx = ix + d.textlength(num + " ", font=f_num)
            d.text((nx, iy + 1), key, font=f_key, fill=INK)
            kx = nx + d.textlength(key + " ", font=f_key)
            first = wrap(d, text, f_item, col_w - (kx - ix))
            d.text((kx, iy + 1), first[0] if first else "", font=f_item, fill=INK)
            if len(first) > 1:
                d.text((ix, iy + 13), first[1], font=f_item, fill=INK)
    y = row_y[8] + 4

    # bottom strip: world map + DATE CHECK
    d.line([(MX, y), (W - MX, y)], fill=INK, width=2)
    y += 6
    map_w, map_h = 200, 99
    m = sage_map(map_w, map_h)
    img.paste(m, (MX + 6, y), m)
    bx = MX + map_w + 30
    bw = W - MX - bx
    box_h = 54
    box_y = y + (map_h - box_h) // 2
    d.rectangle([bx, box_y, bx + bw, box_y + box_h], outline=RED, width=2)
    d.text((bx + 10, box_y + 5), "\u2713  DATE CHECK", font=f_date, fill=DARKRED)
    d.text((bx + 10, box_y + 22), "Every story above happened or was first reported on", font=f_date2, fill=INK)
    d.text((bx + 10, box_y + 37), "Monday 23 November 2026  \u2022  SENIN, 23 NOVEMBER 2026", font=f_date2, fill=INK)
    y += map_h + 6
    d.text((W // 2, y), "Built for make.fun  \u2022  news-image-20261123  \u2022  Photos: Wikimedia Commons (credits in README)",
           font=f_foot, fill=GREY, anchor="ma")
    y += 10
    print("final y =", y, "canvas H =", H)

    out = os.path.join(BASE, "entry.png")
    img.save(out, optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
