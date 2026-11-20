#!/usr/bin/env python3
"""Deterministic meme for gta6-meme-x-01.
Vice City sunset + the REAL make.fun ghost (press-kit mark-1024.png)
worked into the scene. No network, no wall clock, fixed seed.
Output: meme.png (1200x1200) next to this script.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1200
HORIZON = 720
SAND_TOP = 820
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GHOST = "ghost-mark-1024.png"

random.seed(42)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_color(y):
    top = (43, 16, 85)
    mid1 = (150, 30, 120)
    mid2 = (255, 46, 136)
    mid3 = (255, 123, 61)
    t = y / HORIZON
    if t < 0.33:
        return lerp(top, mid1, t / 0.33)
    if t < 0.66:
        return lerp(mid1, mid2, (t - 0.33) / 0.33)
    return lerp(mid2, mid3, (t - 0.66) / 0.34)


img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)

# --- sky gradient ---
for y in range(HORIZON):
    d.line([(0, y), (W, y)], fill=sky_color(y))

# --- stars ---
for _ in range(90):
    x = random.randint(0, W - 1)
    y = random.randint(0, 380)
    if 730 < x < 1030 and 150 < y < 450:
        continue  # keep sun area clear
    r = random.choice([1, 1, 2])
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

# --- retro sun (upper right) with slits ---
sun_cx, sun_cy, sun_r = 880, 300, 140
sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sun)
sd.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
           fill=(255, 222, 130, 255))
# cut horizontal slits through the lower half
for i, yy in enumerate(range(sun_cy + 10, sun_cy + sun_r, 26)):
    half = int(math.sqrt(max(0, sun_r * sun_r - (yy - sun_cy) ** 2)))
    sd.rectangle([sun_cx - half, yy, sun_cx + half, yy + 6 + i * 2],
                 fill=(0, 0, 0, 0))
img = Image.alpha_composite(img.convert("RGBA"), sun)
d = ImageDraw.Draw(img)
# repaint slit gaps with sky colour (they were transparent, sky shows through already)
# (alpha composite over the sky keeps sky visible in slits — nothing to do)

# --- skyline silhouettes on the horizon ---
SIL = (26, 10, 46)
for x0, wdt, hgt in [(0, 90, 60), (95, 60, 95), (160, 80, 45), (245, 55, 80),
                     (940, 70, 85), (1015, 60, 50), (1080, 120, 70)]:
    d.rectangle([x0, HORIZON - hgt, x0 + wdt, HORIZON], fill=SIL)
for _ in range(40):  # lit windows
    x = random.randint(0, 300) if random.random() < 0.5 else random.randint(940, 1195)
    y = random.randint(HORIZON - 85, HORIZON - 8)
    d.rectangle([x, y, x + 5, y + 7], fill=(255, 210, 110))

# --- ocean band ---
for y in range(HORIZON, SAND_TOP):
    t = (y - HORIZON) / (SAND_TOP - HORIZON)
    d.line([(0, y), (W, y)], fill=lerp((64, 32, 110), (24, 16, 70), t))
for yy in (745, 770, 795):
    for _ in range(6):
        x = random.randint(0, 1100)
        d.line([(x, yy), (x + random.randint(40, 110), yy)],
               fill=(255, 150, 120), width=3)

# --- sand ---
for y in range(SAND_TOP, H):
    t = (y - SAND_TOP) / (H - SAND_TOP)
    d.line([(0, y), (W, y)], fill=lerp((255, 196, 138), (228, 148, 104), t))

# --- palm silhouettes ---
PALM = (20, 8, 38)


def bezier(p0, p1, p2, steps=40):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def palm(base_x, crown_x, crown_y, flip):
    d.line(bezier((base_x, H), ((base_x + crown_x) / 2, (H + crown_y) / 2 + 60),
                  (crown_x, crown_y)), fill=PALM, width=22, joint="curve")
    for ang in (-160, -130, -100, -70, -40, -10, 20):
        a = math.radians(ang if not flip else 180 - ang)
        tip = (crown_x + math.cos(a) * 190, crown_y + math.sin(a) * 90 + 55)
        mid = (crown_x + math.cos(a) * 100, crown_y + math.sin(a) * 20 - 25)
        d.line(bezier((crown_x, crown_y), mid, tip), fill=PALM, width=13,
               joint="curve")
    d.ellipse([crown_x - 12, crown_y - 6, crown_x + 12, crown_y + 18], fill=PALM)


palm(70, 210, 760, flip=False)
palm(1130, 990, 740, flip=True)

# --- ghost shadow + real ghost ---
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shd = ImageDraw.Draw(shadow)
shd.ellipse([420, 940, 780, 985], fill=(0, 0, 0, 110))
shadow = shadow.filter(ImageFilter.GaussianBlur(8))
img = Image.alpha_composite(img, shadow)
ghost = Image.open(GHOST).convert("RGBA").resize((560, 560), Image.LANCZOS)
img.paste(ghost, (320, 400), ghost)
d = ImageDraw.Draw(img)


def fit_font(text, size, max_w):
    while size > 20:
        f = ImageFont.truetype(FONT, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(FONT, size)


def outlined_text(cx, y, text, font, fill, stroke_w=10):
    d.text((cx, y), text, font=font, fill=fill, anchor="ma",
           stroke_width=stroke_w, stroke_fill=(10, 5, 25))


# --- top text ---
f1 = fit_font("WAITED 13 YEARS", 118, 1120)
outlined_text(W // 2, 55, "WAITED 13 YEARS", f1, (255, 255, 255))
f2 = fit_font("FOR GTA 6.", 118, 1120)
outlined_text(W // 2, 185, "FOR GTA 6.", f2, (255, 230, 120))

# --- bottom text ---
f3 = fit_font("NOW I GET PAID TO PLAY IT.", 68, 1120)
outlined_text(W // 2, 985, "NOW I GET PAID TO PLAY IT.", f3, (255, 255, 255), 8)

# --- make.fun pill ---
d.rounded_rectangle([385, 1092, 815, 1172], radius=40, fill=(255, 255, 255),
                    outline=(10, 5, 25), width=5)
f4 = ImageFont.truetype(FONT, 62)
d.text((600, 1132), "make.fun", font=f4, fill=(230, 0, 126), anchor="mm")

img.convert("RGB").save("meme.png", "PNG")
print("saved meme.png", img.size)
