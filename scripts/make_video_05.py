import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

import os
OUT = sys.argv[1]
TEST = len(sys.argv) > 2 and sys.argv[2] == "test"  # mode test : quelques images seulement
DUREE = float(os.environ.get("DUREE", "20"))  # Planner 2027 (Avent jour 1), règle 10-30 s
assert 10 <= DUREE <= 30
W, H, FPS = 1080, 1920, 30
N = int(DUREE * FPS)
K = N / 300.0  # échelle des temps (le script est écrit pour 10 s)
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references") + "/"
# ZONE SÛRE (cadrage validé sur TikTok, Instagram, Facebook) : rien ne doit sortir de ce cadre
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 = 150, 930, 260, 1440
MAXW = SAFE_X1 - SAFE_X0 - 20  # largeur maximale d'un élément
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
MED = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
GOLD = (230, 184, 74)
WHITE = (255, 255, 255)
NAVY0, NAVY1 = (9, 24, 66), (15, 34, 100)
DEEP = (6, 12, 40)
SOFT = (130, 170, 255)


def F(p, s):
    return ImageFont.truetype(p, s)


def vgrad(w, h, c0, c1):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line((0, y, w, y), fill=tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3)))
    return im


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), radius=r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def text_img(txt, font, fill, pad=6):
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    b = d0.textbbox((0, 0), txt, font=font)
    w, h = b[2] - b[0] + pad * 2, b[3] - b[1] + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - b[0], pad - b[1]), txt, font=font, fill=fill)
    return im


def pill(txt, font, bg=None, fg=WHITE, outline=None, px=44, py=20, ow=5):
    t = text_img(txt, font, fg, pad=0)
    w, h = t.size[0] + px * 2, t.size[1] + py * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg, outline=outline, width=ow if outline else 0)
    im.alpha_composite(t, (px, py))
    return im


# ---------- ressources fournies ----------
logo_src = Image.open(REF + "logo.png").convert("RGB").crop((222, 222, 1032, 1032)).resize((250, 250), Image.LANCZOS)
lm = Image.new("L", (250, 250), 0)
ImageDraw.Draw(lm).ellipse((0, 0, 249, 249), fill=255)
logo = logo_src.convert("RGBA")
logo.putalpha(lm)

poster = Image.open(REF + "affiche.png").convert("RGB").resize((W, H))
car = Image.open(REF + "carrousel.jpg").convert("RGB")
tiles_box = [(293, 0, 684, 475), (153, 497, 545, 972), (571, 497, 961, 972)]
tiles = []
for b in tiles_box:
    t = car.crop(b)
    t = t.resize((int(t.size[0] * 0.76), int(t.size[1] * 0.76)), Image.LANCZOS)
    tiles.append(rounded(t, 28))

# ---------- fonds ----------
def navy_bg():
    bg = vgrad(W, H, NAVY0, NAVY1).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse((-260, 1180, 420, 1860), fill=(230, 184, 74, 22))
    d.ellipse((700, 120, 1300, 720), fill=(130, 170, 255, 22))
    bg.alpha_composite(ov)
    return bg.convert("RGB")


def collage_bg():
    dark = Image.new("RGB", (W, H), DEEP)
    return Image.blend(poster, dark, 0.62)


# ---------- éléments animés : (image RGBA, x, y, début, type) ----------
def centered_x(im):
    return (W - im.size[0]) // 2



scenes = []
COV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "couvertures") + "/"

def cover(lang="fr", w=460, frame=True):
    c = Image.open(COV + f"planner-2027-{lang}.jpg").convert("RGB")
    c = c.resize((w, int(c.size[1] * w / c.size[0])), Image.LANCZOS)
    if not frame:
        return rounded(c, 14)
    fr = Image.new("RGBA", (c.size[0] + 14, c.size[1] + 14), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle((0, 0, fr.size[0] - 1, fr.size[1] - 1), radius=20, fill=GOLD)
    fr.alpha_composite(rounded(c, 14), (7, 7))
    return fr

def door(n, size=420):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=36, fill=GOLD)
    d.rounded_rectangle((18, 18, size - 19, size - 19), radius=26, outline=DEEP, width=6)
    # ruban
    d.rectangle((size // 2 - 22, 0, size // 2 + 22, size), fill=(180, 40, 50))
    d.rectangle((0, size // 2 - 22, size, size // 2 + 22), fill=(180, 40, 50))
    t = text_img(str(n), F(BOLD, 200), WHITE)
    c = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    ImageDraw.Draw(c).ellipse((0, 0, 219, 219), fill=DEEP)
    c.alpha_composite(t, ((220 - t.size[0]) // 2, (220 - t.size[1]) // 2))
    im.alpha_composite(c, ((size - 220) // 2, (size - 220) // 2))
    return im

def arrow_up(h=90, w=70):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w // 2, 0), (w - 1, h // 2), (w * 0.68, h // 2), (w * 0.68, h - 1), (w * 0.32, h - 1), (w * 0.32, h // 2), (0, h // 2)], fill=GOLD)
    return im

# 1. Miniature : titre en gros + vraie couverture, visible dès l'image 0
e = []
e.append((pill("AVENT · JOUR 1", F(BOLD, 36), bg=GOLD, fg=DEEP, px=36, py=14), None, 275, -30, "fade"))
e.append((text_img("Planner 2027", F(BOLD, 112), WHITE), None, 345, -30, "fade"))
e.append((cover("fr", 440), None, 510, -30, "fade"))
e.append((pill("7,90 € · PDF à imprimer", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1170, -30, "fade"))
scenes.append((navy_bg(), e))

# 2. La case n°1 du calendrier de l'Avent s'ouvre
e = []
e.append((text_img("Calendrier de l'Avent", F(BOLD, 64), WHITE), None, 300, 0, "fade"))
e.append((cover("fr", 300), None, 470, 28, "pop"))
e.append((door(1, 440), None, 450, 14, "open"))
e.append((text_img("L'idée cadeau du jour", F(BOLD, 58), GOLD), None, 1000, 30, "slide"))
e.append((text_img("Une année bien rangée", F(MED, 50), WHITE), None, 1110, 40, "fade"))
scenes.append((navy_bg(), e))

# 3. Ce qu'il contient
e = []
e.append((pill("DANS LE PDF", F(BOLD, 34), bg=GOLD, fg=DEEP, px=36, py=14), None, 290, 0, "fade"))
e.append((text_img("80 pages", F(BOLD, 130), WHITE), None, 400, 6, "slide"))
e.append((text_img("format A4", F(BOLD, 80), GOLD), None, 570, 14, "slide"))
e.append((pill("12 mois : calendrier, priorités", F(BOLD, 38), outline=GOLD, fg=GOLD, px=36, py=18), None, 760, 24, "pop"))
e.append((pill("52 semaines datées", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 885, 34, "pop"))
e.append((pill("Objectifs, budget, habitudes", F(BOLD, 38), outline=GOLD, fg=GOLD, px=36, py=18), None, 1010, 44, "pop"))
e.append((text_img("Du lundi au dimanche", F(MED, 46), WHITE), None, 1150, 52, "fade"))
scenes.append((navy_bg(), e))

# 4. Disponible en 7 langues : les 7 vraies couvertures
e = []
e.append((text_img("Disponible", F(BOLD, 96), WHITE), None, 290, 0, "slide"))
e.append((text_img("en 7 langues", F(BOLD, 96), GOLD), None, 420, 8, "slide"))
langs = ["fr", "en", "es", "de", "it", "nl", "pt"]
cw = 168
row1 = langs[:4]; row2 = langs[4:]
x0 = (W - (4 * (cw + 14) - 14)) // 2
for k, l in enumerate(row1):
    e.append((cover(l, cw, frame=False), x0 + k * (cw + 14), 600, 14 + k * 4, "pop"))
x1 = (W - (3 * (cw + 14) - 14)) // 2
for k, l in enumerate(row2):
    e.append((cover(l, cw, frame=False), x1 + k * (cw + 14), 860, 30 + k * 4, "pop"))
e.append((text_img("FR · EN · ES · DE · IT · NL · PT", F(BOLD, 40), WHITE), None, 1150, 46, "fade"))
scenes.append((navy_bg(), e))

# 5. La marketplace
e = []
e.append((logo.resize((170, 170), Image.LANCZOS), None, 300, 0, "pop"))
e.append((text_img("Téléchargement", F(BOLD, 96), WHITE), None, 510, 8, "slide"))
e.append((text_img("immédiat", F(BOLD, 110), GOLD), None, 650, 16, "slide"))
e.append((pill("Un seul compte", F(BOLD, 42), bg=GOLD, fg=DEEP, px=42, py=20), None, 870, 28, "pop"))
e.append((pill("Achète et vends", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1000, 38, "pop"))
e.append((pill("Inscription gratuite", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1125, 48, "pop"))
scenes.append((navy_bg(), e))

# 6. Appel à l'action
e = []
e.append((cover("fr", 330), None, 285, 0, "pop"))
e.append((text_img("Tu l'imprimes", F(BOLD, 72), WHITE), None, 790, 10, "slide"))
e.append((text_img("pour janvier ?", F(BOLD, 72), GOLD), None, 885, 16, "slide"))
e.append((arrow_up(), None, 1010, 26, "pop"))
e.append((pill("Lien dans la bio", F(BOLD, 50), bg=GOLD, fg=DEEP, px=50, py=22), None, 1115, 26, "pop"))
e.append((text_img("livriko.com", F(BOLD, 44), WHITE), None, 1270, 36, "fade"))
scenes.append((navy_bg(), e))

NS = len(scenes)

# sécurité : tout élément trop large est réduit pour rester dans la zone sûre
def fit(im):
    if im.size[0] <= MAXW:
        return im
    r = MAXW / im.size[0]
    return im.resize((MAXW, max(1, int(im.size[1] * r))), Image.LANCZOS)


scenes = [(bg, [(fit(im), x, y, st, k) for (im, x, y, st, k) in els]) for (bg, els) in scenes]


import random
_r = random.Random(7)
FLAKES = [(_r.randint(SAFE_X0, SAFE_X1), _r.uniform(0, H), _r.uniform(60, 140), _r.randint(3, 8), _r.uniform(0, 6.28)) for _ in range(60)]

def snow(frame, fi):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x, y0, sp, r, ph in FLAKES:
        y = (y0 + sp * fi / FPS) % H
        xx = x + 25 * math.sin(ph + fi / 40.0)
        xx = min(max(xx, SAFE_X0), SAFE_X1)
        d.ellipse((xx - r, y - r, xx + r, y + r), fill=(255, 255, 255, 120))
    frame.alpha_composite(ov)

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def render(fi):
    SL = N / NS
    si = min(NS - 1, int(fi // SL))
    lf = (fi - si * SL) / (SL / 75.0)
    bg, els = scenes[si]
    frame = bg.convert("RGBA")
    snow(frame, fi)
    for im, x, y, start, kind in els:
        p = ease((lf - start) / 14.0)
        if p <= 0 and kind != "open":
            continue
        xx = centered_x(im) if x is None else x
        yy = y
        src = im
        a = p
        if kind == "slide":
            yy = y + int((1 - p) * 70)
        elif kind == "fade":
            yy = y + int((1 - p) * 24)
        elif kind == "pop":
            s = 0.82 + 0.18 * p
            nw, nh = max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))
            src = im.resize((nw, nh), Image.BICUBIC)
            xx = (W - nw) // 2 if x is None else x + (im.size[0] - nw) // 2
            yy = y + (im.size[1] - nh) // 2
        elif kind == "open":
            a = 1 - p
            s2 = 1 + 0.35 * p
            nw, nh = max(1, int(im.size[0] * s2)), max(1, int(im.size[1] * s2))
            src = im.resize((nw, nh), Image.BICUBIC)
            xx = (W - nw) // 2 if x is None else x
            yy = y + (im.size[1] - nh) // 2
            if a <= 0.01:
                continue
        if a < 1:
            al = src.getchannel("A").point(lambda v: int(v * a))
            src = src.copy()
            src.putalpha(al)
        frame.alpha_composite(src, (xx, yy))
    # léger zoom lent sur chaque plan
    z = 1 + 0.025 * (lf / 100.0)
    cw, ch = W / z, H / z
    box = ((W - cw) / 2, (H - ch) * 0.35, (W + cw) / 2, (H - ch) * 0.35 + ch)
    return frame.convert("RGB").resize((W, H), Image.BICUBIC, box=box)


if TEST:
    for fi in [int((i + 0.9) * N / NS) for i in range(NS)]:
        render(fi).save(f"{OUT}/test_{fi}.png")
    print("test ok")
else:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(DUREE), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "64k", "-shortest", "-movflags", "+faststart", f"{OUT}/video_pro.mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(N):
        pr.stdin.write(render(fi).tobytes())
    pr.stdin.close()
    pr.wait()
    print("video ok")
