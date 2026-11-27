import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

import os
OUT = sys.argv[1]
TEST = len(sys.argv) > 2 and sys.argv[2] == "test"  # mode test : quelques images seulement
DUREE = float(os.environ.get("DUREE", "45"))  # vidéo spéciale « Le guide de LIVRIKO » : 45 s autorisées par l’utilisateur (27/11) pour cette vidéo seulement
assert DUREE <= 50
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
GUIDE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "guide-livriko") + "/"

def page(n, w=600):
    c = Image.open(GUIDE + f"page-{n:02d}.jpg").convert("RGB")
    c = c.resize((w, int(c.size[1] * w / c.size[0])), Image.LANCZOS)
    fr = Image.new("RGBA", (c.size[0] + 16, c.size[1] + 16), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle((0, 0, fr.size[0] - 1, fr.size[1] - 1), radius=18, fill=GOLD)
    fr.alpha_composite(rounded(c, 12), (8, 8))
    return fr

# 1. Nouveau : le guide offert
e = []
e.append((pill("NOUVEAU · OFFERT", F(BOLD, 36), bg=GOLD, fg=DEEP, px=36, py=14), None, 300, 0, "fade"))
e.append((logo.resize((220, 220), Image.LANCZOS), None, 430, 6, "pop"))
e.append((text_img("Le guide", F(BOLD, 120), WHITE), None, 690, 14, "slide"))
e.append((text_img("de LIVRIKO", F(BOLD, 110), GOLD), None, 850, 24, "slide"))
e.append((text_img("Tout comprendre du site", F(MED, 46), WHITE), None, 1040, 36, "fade"))
e.append((pill("16 pages · PDF gratuit", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1160, 46, "pop"))
scenes.append((navy_bg(), e))

# 2. La couverture du guide
e = []
e.append((pill("LE GUIDE EN PDF", F(BOLD, 32), bg=GOLD, fg=DEEP, px=34, py=14), None, 280, 0, "fade"))
e.append((page(1, 640), None, 370, 6, "slide"))
scenes.append((navy_bg(), e))

# 3. La boutique
e = []
e.append((pill("LA BOUTIQUE", F(BOLD, 34), bg=GOLD, fg=DEEP, px=36, py=14), None, 300, 0, "fade"))
e.append((text_img("10 catégories", F(BOLD, 96), WHITE), None, 470, 8, "slide"))
e.append((text_img("7 langues", F(BOLD, 110), GOLD), None, 620, 18, "slide"))
e.append((pill("Moteur de recherche", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 880, 30, "pop"))
e.append((pill("Aperçu offert avant l'achat", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1010, 40, "pop"))
e.append((pill("Avis des lecteurs", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1140, 50, "pop"))
scenes.append((navy_bg(), e))

# 4. Un seul compte
e = []
e.append((logo.resize((180, 180), Image.LANCZOS), None, 320, 0, "pop"))
e.append((text_img("UN SEUL COMPTE", F(BOLD, 46), SOFT), None, 550, 6, "fade"))
e.append((text_img("Acheter", F(BOLD, 128), WHITE), None, 640, 12, "slide"))
e.append((text_img("et vendre", F(BOLD, 128), GOLD), None, 805, 22, "slide"))
e.append((pill("Création gratuite", F(BOLD, 44), bg=GOLD, fg=DEEP, px=44, py=20), None, 1050, 34, "pop"))
e.append((pill("Ma bibliothèque", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1180, 44, "pop"))
scenes.append((navy_bg(), e))

# 5. Acheter et télécharger
e = []
e.append((pill("ACHETER", F(BOLD, 34), bg=GOLD, fg=DEEP, px=36, py=14), None, 300, 0, "fade"))
e.append((text_img("Paiement", F(BOLD, 110), WHITE), None, 450, 8, "slide"))
e.append((text_img("sécurisé", F(BOLD, 110), GOLD), None, 600, 18, "slide"))
e.append((text_img("par Stripe", F(MED, 60), WHITE), None, 760, 28, "fade"))
e.append((pill("Téléchargement immédiat", F(BOLD, 42), bg=GOLD, fg=DEEP, px=42, py=20), None, 960, 38, "pop"))
e.append((pill("PDF · à tout moment", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1100, 48, "pop"))
scenes.append((navy_bg(), e))

# 6. Une page du guide : vendre
e = []
e.append((pill("DANS LE GUIDE", F(BOLD, 32), bg=GOLD, fg=DEEP, px=34, py=14), None, 280, 0, "fade"))
e.append((page(12, 640), None, 370, 6, "slide"))
scenes.append((navy_bg(), e))

# 7. Vendre : 85 %
e = []
e.append((pill("VENDRE SUR LIVRIKO", F(BOLD, 34), bg=GOLD, fg=DEEP, px=36, py=14), None, 300, 0, "fade"))
e.append((text_img("Vous gardez", F(BOLD, 84), WHITE), None, 430, 8, "slide"))
e.append((text_img("85 %", F(BOLD, 200), GOLD), None, 540, 18, "pop"))
e.append((pill("Aucune candidature", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 860, 30, "pop"))
e.append((pill("Votre prix · 1 € minimum", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 990, 40, "pop"))
e.append((pill("En ligne immédiatement", F(BOLD, 40), outline=GOLD, fg=GOLD, px=40, py=18), None, 1120, 50, "pop"))
scenes.append((navy_bg(), e))

# 8. 3 mois offerts
e = []
e.append((pill("NOUVEAU VENDEUR", F(BOLD, 34), bg=GOLD, fg=DEEP, px=36, py=14), None, 300, 0, "fade"))
e.append((text_img("3 mois", F(BOLD, 170), GOLD), None, 450, 8, "pop"))
e.append((text_img("offerts", F(BOLD, 120), WHITE), None, 680, 18, "slide"))
e.append((text_img("pour tester", F(MED, 64), WHITE), None, 860, 28, "fade"))
e.append((pill("Sans carte bancaire", F(BOLD, 44), bg=GOLD, fg=DEEP, px=44, py=20), None, 1040, 40, "pop"))
scenes.append((navy_bg(), e))

# 9. Appel à l'action
e = []
e.append((page(1, 380), None, 290, 0, "pop"))
e.append((text_img("Le guide est gratuit", F(BOLD, 68), WHITE), None, 840, 14, "slide"))
e.append((pill("Téléchargement gratuit", F(BOLD, 44), bg=GOLD, fg=DEEP, px=44, py=20), None, 980, 28, "pop"))
e.append((pill("Sur livriko.com", F(BOLD, 52), outline=GOLD, fg=GOLD, px=56, py=22, ow=6), None, 1120, 40, "pop"))
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
        if p <= 0:
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
