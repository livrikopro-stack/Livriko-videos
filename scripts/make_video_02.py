import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

import os
OUT = sys.argv[1]
TEST = len(sys.argv) > 2 and sys.argv[2] == "test"  # mode test : quelques images seulement
DUREE = float(os.environ.get("DUREE", "10"))  # secondes (entre 5 et 20 ; jamais plus de 20)
assert DUREE <= 20  # plafond fixé par l’utilisateur : entre 5 et 20 secondes
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

def cover(name, w=560):
    c = Image.open(COV + name).convert("RGB")
    c = c.resize((w, int(c.size[1] * w / c.size[0])), Image.LANCZOS)
    fr = Image.new("RGBA", (c.size[0] + 16, c.size[1] + 16), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle((0, 0, fr.size[0] - 1, fr.size[1] - 1), radius=18, fill=GOLD)
    fr.alpha_composite(rounded(c, 12), (8, 8))
    return fr

# SCÈNE 1 : Noël sur la marketplace
els1 = []
els1.append((pill("NOËL SUR LA MARKETPLACE", F(BOLD, 36), bg=GOLD, fg=DEEP, px=36, py=14), None, 290, 0, "fade"))
els1.append((logo.resize((220, 220), Image.LANCZOS), None, 440, 6, "pop"))
els1.append((text_img("LIVRIKO", F(BOLD, 128), GOLD), None, 700, 14, "fade"))
els1.append((text_img("Idées de Noël", F(BOLD, 84), WHITE), None, 900, 26, "slide"))
els1.append((text_img("à télécharger", F(BOLD, 84), GOLD), None, 1010, 36, "slide"))
els1.append((pill("PDF · Téléchargement immédiat", F(MED, 30), outline=GOLD, fg=GOLD, px=28, py=14), None, 1220, 50, "pop"))
scenes.append((navy_bg(), els1))

def book_scene(fn, tag, title, price):
    els = []
    els.append((pill(tag, F(BOLD, 32), bg=GOLD, fg=DEEP, px=34, py=14), None, 285, 0, "fade"))
    els.append((cover(fn), None, 380, 6, "slide"))
    els.append((text_img(title, F(BOLD, 52), WHITE), None, 1215, 30, "fade"))
    els.append((pill(price, F(BOLD, 56), bg=GOLD, fg=DEEP, px=50, py=16), None, 1310, 42, "pop"))
    return (navy_bg(), els)

scenes.append(book_scene("mon-premier-noel-fr.jpg", "LIVRE SOUVENIR · EN PDF", "Mon premier Noël", "5,90 €"))
scenes.append(book_scene("mon-livre-de-noel-a-colorier-fr.jpg", "À COLORIER · EN PDF", "Livre de Noël à colorier", "3,90 €"))

# SCÈNE 4 : un seul compte
bg3 = navy_bg()
els3 = []
els3.append((logo.resize((180, 180), Image.LANCZOS), None, 330, 0, "pop"))
els3.append((text_img("UN SEUL COMPTE", F(BOLD, 46), SOFT), None, 560, 6, "fade"))
els3.append((text_img("Acheter", F(BOLD, 128), WHITE), None, 650, 12, "slide"))
els3.append((text_img("et vendre", F(BOLD, 128), GOLD), None, 815, 22, "slide"))
els3.append((pill("Inscription gratuite", F(BOLD, 44), bg=GOLD, fg=DEEP, px=44, py=20), None, 1050, 32, "pop"))
els3.append((pill("Sans carte bancaire", F(BOLD, 38), outline=GOLD, fg=GOLD, px=40, py=18), None, 1170, 42, "pop"))
els3.append((pill("Sur livriko.com", F(BOLD, 48), outline=GOLD, fg=GOLD, px=56, py=22, ow=6), None, 1300, 52, "pop"))
scenes.append((bg3, els3))


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
    SL = N / 4.0
    si = min(3, int(fi // SL))
    lf = (fi - si * SL) / K
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
    for fi in (int(N*0.31), int(N*0.64), int(N*0.97)):
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
