import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

OUT = sys.argv[1]
TEST = len(sys.argv) > 2  # mode test : quelques images seulement
W, H, FPS, N = 1080, 1920, 30, 300
U = "/mnt/user-data/uploads/"
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
logo_src = Image.open(U + "95428702-image.png").convert("RGB").crop((222, 222, 1032, 1032)).resize((250, 250), Image.LANCZOS)
lm = Image.new("L", (250, 250), 0)
ImageDraw.Draw(lm).ellipse((0, 0, 249, 249), fill=255)
logo = logo_src.convert("RGBA")
logo.putalpha(lm)

poster = Image.open(U + "edf28942-image.png").convert("RGB").resize((W, H))
car = Image.open(U + "ee086511-image.jpg").convert("RGB")
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

# SCÈNE 1 : la marketplace
bg1 = collage_bg()
d = ImageDraw.Draw(bg1)
d.rounded_rectangle((120, 300, 960, 1600), radius=64, fill=DEEP, outline=GOLD, width=8)
els1 = []
els1.append((pill("LA MARKETPLACE", F(BOLD, 46), bg=GOLD, fg=DEEP, px=50, py=18), None, 250, 0, "fade"))
els1.append((logo, None, 350, 6, "pop"))
els1.append((text_img("LIVRIKO", F(BOLD, 150), GOLD), None, 630, 14, "fade"))
els1.append((text_img("UN MONDE NUMÉRIQUE À DÉCOUVRIR", F(MED, 36), SOFT), None, 820, 22, "fade"))
els1.append((text_img("Acheter.", F(BOLD, 128), WHITE), None, 910, 34, "slide"))
els1.append((text_img("Vendre.", F(BOLD, 128), GOLD), None, 1080, 48, "slide"))
els1.append((pill("PDF · Téléchargement immédiat", F(MED, 38), outline=GOLD, fg=GOLD, px=36, py=16), None, 1290, 66, "pop"))
scenes.append((bg1, els1))

# SCÈNE 2 : des livres pour tous les goûts
bg2 = navy_bg()
d = ImageDraw.Draw(bg2)
d.rounded_rectangle((50, 340, 1030, 840), radius=60, fill=(20, 42, 120), outline=GOLD, width=9)
els2 = []
els2.append((pill("DES LIVRES POUR TOUS LES GOÛTS", F(BOLD, 40), bg=GOLD, fg=DEEP, px=44, py=16), None, 250, 0, "fade"))
tw = tiles[0].size[0]
gap = 20
x0 = (W - (3 * tw + 2 * gap)) // 2
for i, t in enumerate(tiles):
    els2.append((t, x0 + i * (tw + gap), 410, 8 + i * 8, "slide"))
els2.append((text_img("Cuisine · Voyage · Famille", F(BOLD, 62), WHITE), None, 900, 36, "fade"))
els2.append((text_img("Business · Bien-être · Loisirs…", F(BOLD, 62), GOLD), None, 990, 44, "fade"))
els2.append((pill("Gratuits ou payants", F(BOLD, 46), bg=GOLD, fg=DEEP, px=52, py=20), None, 1140, 58, "pop"))
els2.append((text_img("Livrets, guides et e-books en PDF", F(MED, 42), WHITE), None, 1290, 70, "fade"))
scenes.append((bg2, els2))

# SCÈNE 3 : un seul compte
bg3 = navy_bg()
els3 = []
els3.append((logo.resize((190, 190), Image.LANCZOS), None, 250, 0, "pop"))
els3.append((text_img("UN SEUL COMPTE", F(BOLD, 52), SOFT), None, 480, 8, "fade"))
els3.append((text_img("Acheter", F(BOLD, 160), WHITE), None, 570, 16, "slide"))
els3.append((text_img("et vendre", F(BOLD, 160), GOLD), None, 760, 28, "slide"))
els3.append((pill("Inscription gratuite", F(BOLD, 50), bg=GOLD, fg=DEEP, px=54, py=22), None, 1030, 44, "pop"))
els3.append((pill("Sans carte bancaire", F(BOLD, 44), outline=GOLD, fg=GOLD, px=50, py=20), None, 1170, 56, "pop"))
d3 = bg3
els3.append((pill("Sur livriko.com", F(BOLD, 62), outline=GOLD, fg=GOLD, px=90, py=26, ow=6), None, 1340, 70, "pop"))
scenes.append((bg3, els3))


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def render(fi):
    si = min(2, fi // 100)
    lf = fi - si * 100
    bg, els = scenes[si]
    frame = bg.convert("RGBA")
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
    z = 1 + 0.035 * (lf / 100.0)
    cw, ch = W / z, H / z
    box = ((W - cw) / 2, (H - ch) * 0.35, (W + cw) / 2, (H - ch) * 0.35 + ch)
    return frame.convert("RGB").resize((W, H), Image.BICUBIC, box=box)


if TEST:
    for fi in (45, 160, 285):
        render(fi).save(f"{OUT}/test_{fi}.png")
    print("test ok")
else:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "10", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "64k", "-shortest", "-movflags", "+faststart", f"{OUT}/video_pro.mp4"]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(N):
        pr.stdin.write(render(fi).tobytes())
    pr.stdin.close()
    pr.wait()
    print("video ok")
