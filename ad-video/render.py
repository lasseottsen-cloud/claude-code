"""
Handwerk Ad Video Renderer v3 — 2-Minuten Cut
~120 seconds @ 30fps = 3590 frames @ 1280x720

Narrative arc:
  ACT 1 — Problem       (S0–S4):   Fragmentierte Tools, Chaos, Freeze, Node emerges, Dissolve
  ACT 2 — Platform Live (S5–S12):  Dashboard, Kanban, Zeiterfassung, Ticketsystem,
                                    Dokumente, Kalkulation, Buchhaltung, Mobile
  ACT 3 — Social Proof  (S13–S16): Warenwirtschaft, Projektverwaltung, ISOTEC/VITERMA, Zitat
  ACT 4 — Vision        (S17–S19): Full overview, Finale tagline, Outro
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
import math
import os

# ─── Config ───────────────────────────────────────────────────────────────────
W, H = 1280, 720
FPS  = 30
OUT_PATH = os.path.join(os.path.dirname(__file__), "out", "ad-video.mp4")
os.makedirs(os.path.join(os.path.dirname(__file__), "out"), exist_ok=True)

# Scene lengths in frames
SCENE_LENGTHS = [
    150,  # S0  — Icons isolated            (extended)
    180,  # S1  — Chaos lines               (extended)
    160,  # S2  — Freeze / overwhelm        (extended)
    200,  # S3  — Node emerges              (extended)
    200,  # S4  — Integration dissolve      (extended)
    210,  # S5  — Dashboard UI              (extended)
    210,  # S6  — Kanban Pipeline           (extended)
    180,  # S7  — Zeiterfassung Live        (extended)
    160,  # S8  — Ticketsystem / E-Mail     (extended)
    180,  # S9  — Dokumente & Archiv        (NEW)
    170,  # S10 — Kalkulation / BLS-Import  (NEW)
    160,  # S11 — Buchhaltung / BMD-Sync    (NEW)
    180,  # S12 — Mobile / Baustelle        (NEW)
    150,  # S13 — Warenwirtschaft deep-dive (extended)
    150,  # S14 — Projektverwaltung         (extended)
    200,  # S15 — Social Proof ISOTEC/VITERMA (extended)
    200,  # S16 — Kundenzitat               (NEW)
    200,  # S17 — Full abstract overview    (extended)
    230,  # S18 — Finale tagline            (extended)
    120,  # S19 — Logo Outro               (NEW)
]
TOTAL_FRAMES = sum(SCENE_LENGTHS)   # 3590

# Precompute scene start offsets
SCENE_STARTS = []
_s = 0
for sl in SCENE_LENGTHS:
    SCENE_STARTS.append(_s)
    _s += sl

# ─── Colors ───────────────────────────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
CYAN    = (0, 200, 255)
BLUE    = (0, 120, 255)
PURPLE  = (123, 79, 255)
GRAY    = (140, 150, 180)
LGRAY   = (200, 205, 215)
RED     = (204, 30, 30)     # ISOTEC red
TEAL    = (0, 185, 175)     # VITERMA teal
ORANGE  = (255, 107, 53)
AMBER   = (255, 152, 0)
GREEN   = (33, 150, 80)

# ─── Fonts ────────────────────────────────────────────────────────────────────
_FONT_CACHE = {}
def font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        fname = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
                 else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        try:
            _FONT_CACHE[key] = ImageFont.truetype(fname, size)
        except:
            _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]

# ─── Animation helpers ────────────────────────────────────────────────────────
def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def lerp(frame, f0, f1, v0=0.0, v1=1.0):
    if f1 == f0: return v1 if frame >= f1 else v0
    return v0 + (v1 - v0) * clamp((frame - f0) / (f1 - f0))

def ease_out(t):
    return 1 - (1-t)**3

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def lerp_e(frame, f0, f1, v0=0.0, v1=1.0):
    t = clamp((frame - f0) / max(f1 - f0, 1))
    return v0 + (v1 - v0) * ease_in_out(t)

def lerp_eo(frame, f0, f1, v0=0.0, v1=1.0):
    t = clamp((frame - f0) / max(f1 - f0, 1))
    return v0 + (v1 - v0) * ease_out(t)

def spring(frame, start, stiffness=0.3, damping=0.7):
    t = max(0, frame - start) / FPS
    if t <= 0: return 0.0
    omega = math.sqrt(stiffness) * 15
    zeta  = damping
    if zeta < 1:
        wd  = omega * math.sqrt(1 - zeta**2)
        val = 1 - math.exp(-zeta*omega*t) * (
            math.cos(wd*t) + (zeta*omega/wd)*math.sin(wd*t))
    else:
        val = 1 - math.exp(-omega*t) * (1 + omega*t)
    return clamp(val)

# ─── Icon layout ──────────────────────────────────────────────────────────────
ICON_NORM = {
    "BLS":       (0.15, 0.22),
    "BMD":       (0.80, 0.20),
    "Sevdesk":   (0.09, 0.55),
    "Excel":     (0.88, 0.52),
    "OneDrive":  (0.18, 0.80),
    "Dropbox":   (0.76, 0.80),
    "Email":     (0.44, 0.14),
    "Craftnote": (0.56, 0.85),
}
CENTER_PX = (W//2, H//2)

ICON_META = {
    "BLS":       {"color": ORANGE,         "label": "BLS"},
    "BMD":       {"color": (229, 57, 53),  "label": "BMD"},
    "Sevdesk":   {"color": (0, 188, 212),  "label": "Sevdesk"},
    "Excel":     {"color": GREEN,          "label": "Excel"},
    "OneDrive":  {"color": (0, 120, 212),  "label": "OneDrive"},
    "Dropbox":   {"color": (0, 97, 255),   "label": "Dropbox"},
    "Email":     {"color": (156, 39, 176), "label": "E-Mail"},
    "Craftnote": {"color": AMBER,          "label": "Craftnote"},
}
ALL_ICONS = list(ICON_META.keys())

CONNECTIONS = [
    ("Excel", "BMD"), ("Email", "Craftnote"),
    ("Dropbox", "BLS"), ("OneDrive", "Sevdesk"),
    ("BLS", "Craftnote"), ("BMD", "Email"),
    ("Sevdesk", "Excel"), ("OneDrive", "BMD"),
    ("Dropbox", "Email"), ("Excel", "Craftnote"),
    ("BLS", "Sevdesk"), ("Dropbox", "BMD"),
]
LINE_COLORS = [CYAN, BLUE, PURPLE, ORANGE, AMBER,
               CYAN, BLUE, PURPLE, (0,188,212), CYAN, BLUE, PURPLE]

def icon_px(name):
    nx, ny = ICON_NORM[name]
    return (int(nx * W), int(ny * H))

# ─── Base drawing primitives ──────────────────────────────────────────────────
def make_background():
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:] = (3, 3, 15)
    cx, cy = W//2, H//2
    x = np.arange(W); y = np.arange(H)
    xx, yy = np.meshgrid(x, y)
    dist = np.sqrt((xx-cx)**2 + (yy-cy)**2)
    glow = np.clip(1.0 - dist / (max(W,H)*0.6), 0, 1) * 14
    img[:,:,2] = np.clip(img[:,:,2] + glow*1.8, 0, 255).astype(np.uint8)
    img[:,:,0] = np.clip(img[:,:,0] + glow*0.4, 0, 255).astype(np.uint8)
    return img

def composite(img_pil: Image.Image, layer: Image.Image):
    img_a = img_pil.convert("RGBA")
    img_pil.paste(Image.alpha_composite(img_a, layer).convert("RGB"))

def new_layer():
    return Image.new("RGBA", (W, H), (0,0,0,0))

def draw_icon(img_pil, name, cx, cy, opacity=1.0, scale=1.0, glowing=False):
    if opacity <= 0.01 or scale <= 0.01: return
    size = int(70 * scale)
    half = size // 2
    meta = ICON_META[name]
    color = meta["color"]
    label = meta["label"]
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    if glowing or opacity > 0.5:
        for gi in range(4, 0, -1):
            ga = int(25 * gi/4 * opacity)
            gr = half + 20 + (4-gi)*10
            d.ellipse([cx-gr, cy-gr, cx+gr, cy+gr], fill=(*color, ga))
    x0,y0 = cx-half, cy-half
    x1,y1 = cx+half, cy+half
    d.rounded_rectangle([x0,y0,x1,y1], radius=int(14*scale),
                        fill=(*color, int(28*opacity)),
                        outline=(*color, int(110*opacity)), width=2)
    dot_r = int(5*scale)
    d.ellipse([x1-dot_r*2-2, y1-dot_r*2-2, x1-2, y1-2],
              fill=(*color, int(190*opacity)))
    d.text((cx, cy-int(4*scale)), label[:2], font=font(int(20*scale), bold=True),
           anchor="mm", fill=(*WHITE, int(215*opacity)))
    d.text((cx, cy+half+int(10*scale)), label, font=font(int(10*scale)),
           anchor="mm", fill=(*GRAY, int(170*opacity)))
    composite(img_pil, layer)

def draw_line(img_pil, x1,y1,x2,y2, progress=1.0, color=CYAN,
              width=2, opacity=1.0):
    if progress<=0 or opacity<=0.01: return
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    ex = int(x1 + (x2-x1)*progress)
    ey = int(y1 + (y2-y1)*progress)
    if opacity > 0.25:
        d.line([(x1,y1),(ex,ey)], fill=(*color, int(55*opacity)), width=width*4)
    d.line([(x1,y1),(ex,ey)], fill=(*color, int(245*opacity)), width=width)
    composite(img_pil, layer)

def draw_glow_node(img_pil, cx, cy, scale=1.0, opacity=1.0, pulse=0.0):
    if opacity<=0.01 or scale<=0.01: return
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    for r,a in [(90,20),(60,36),(36,56),(20,82)]:
        r2 = int(r*scale)
        d.ellipse([cx-r2,cy-r2,cx+r2,cy+r2], fill=(*BLUE, int(a*opacity)))
    if pulse > 0:
        pr = int((24+(90-24)*pulse)*scale)
        pa = int((1-pulse)*210*opacity)
        d.ellipse([cx-pr,cy-pr,cx+pr,cy+pr],
                  fill=None, outline=(*CYAN, pa), width=2)
    cr = int(20*scale)
    d.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], fill=(*WHITE, int(235*opacity)))
    dr = int(6*scale)
    d.ellipse([cx-dr,cy-dr,cx+dr,cy+dr], fill=(*BLUE, int(195*opacity)))
    composite(img_pil, layer)

def draw_particles(img_pil, cx, cy, progress, count=28, seed=42, color=AMBER):
    if progress<=0: return
    rng = np.random.default_rng(seed)
    angles = rng.uniform(0, 2*math.pi, count)
    speeds = rng.uniform(60, 180, count)
    sizes  = rng.uniform(2, 6, count)
    layer  = new_layer()
    d      = ImageDraw.Draw(layer)
    for i in range(count):
        dist = speeds[i]*progress
        x = cx + int(math.cos(angles[i])*dist)
        y = cy + int(math.sin(angles[i])*dist)
        alpha = max(0, 1-progress*1.3)
        r = max(1, int(sizes[i]*(1-progress*0.5)))
        d.ellipse([x-r,y-r,x+r,y+r], fill=(*color, int(alpha*215)))
    composite(img_pil, layer)

def text_c(draw, text, y, opacity=1.0, size=14, color=GRAY, bold=False):
    if opacity<=0.01: return
    draw.text((W//2, y), text, font=font(size, bold=bold),
              anchor="mm", fill=(*color, int(255*opacity)))

def draw_module_card(img_pil, cx, cy, title, items, opacity=1.0,
                     color=CYAN, w=200):
    if opacity<=0.01: return
    h_card = 48 + len(items)*22
    x0,y0 = cx-w//2, cy-h_card//2
    x1,y1 = cx+w//2, cy+h_card//2
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0,y0,x1,y1], radius=10,
                        fill=(10,12,30, int(210*opacity)),
                        outline=(*color, int(95*opacity)), width=1)
    d.rounded_rectangle([x0,y0,x1,y0+28], radius=10,
                        fill=(*color, int(38*opacity)))
    d.rounded_rectangle([x0,y0+18,x1,y0+28], radius=0,
                        fill=(*color, int(38*opacity)))
    d.ellipse([x0+8,y0+10,x0+18,y0+20], fill=(*color, int(220*opacity)))
    d.text((x0+26,y0+14), title, font=font(11,bold=True), anchor="lm",
           fill=(*WHITE, int(225*opacity)))
    for i,item in enumerate(items):
        iy = y0+38+i*20
        d.ellipse([x0+10,iy-3,x0+16,iy+3], fill=(*color, int(145*opacity)))
        d.text((x0+24,iy), item, font=font(10), anchor="lm",
               fill=(*GRAY, int(185*opacity)))
    composite(img_pil, layer)

# ─── UI Scene helpers (light/dark card UI) ────────────────────────────────────
def draw_ui_panel(img_pil, x0, y0, w, h, title,
                  opacity=1.0, accent=CYAN, dark=True):
    """Renders a realistic platform UI panel."""
    if opacity<=0.01: return
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    bg   = (12,14,32,int(230*opacity))  if dark else (240,242,248,int(235*opacity))
    bord = (*accent, int(80*opacity))
    d.rounded_rectangle([x0,y0,x0+w,y0+h], radius=8, fill=bg, outline=bord, width=1)
    # Title bar
    bar_col = (*accent, int(35*opacity))
    d.rounded_rectangle([x0,y0,x0+w,y0+30], radius=8, fill=bar_col)
    d.rounded_rectangle([x0,y0+20,x0+w,y0+30], radius=0, fill=bar_col)
    tc = (*WHITE,int(220*opacity)) if dark else (30,30,50,int(220*opacity))
    d.text((x0+12, y0+15), title, font=font(11,bold=True), anchor="lm", fill=tc)
    composite(img_pil, layer)

def draw_ui_stat(img_pil, cx, cy, value, label,
                 opacity=1.0, color=WHITE, vsize=28):
    """Big stat number + small label."""
    if opacity<=0.01: return
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    d.text((cx,cy),   value, font=font(vsize,bold=True),
           anchor="mm", fill=(*color, int(245*opacity)))
    d.text((cx,cy+20), label, font=font(9),
           anchor="mm", fill=(*GRAY, int(185*opacity)))
    composite(img_pil, layer)

def draw_status_badge(img_pil, x, y, text, color, opacity=1.0):
    if opacity<=0.01: return
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    tw = font(9).getlength(text) + 10
    d.rounded_rectangle([x, y-8, x+tw, y+8], radius=4,
                        fill=(*color, int(60*opacity)),
                        outline=(*color, int(130*opacity)), width=1)
    d.text((x+tw//2, y), text, font=font(9), anchor="mm",
           fill=(*color, int(220*opacity)))
    composite(img_pil, layer)

def draw_row(img_pil, x, y, w, text_left, text_right="", opacity=1.0,
             color=LGRAY, accent=None, h=18):
    if opacity<=0.01: return
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x,y-h//2,x+w,y+h//2], radius=3,
                        fill=(255,255,255,int(8*opacity)))
    tc = (*color, int(200*opacity))
    d.text((x+8,y), text_left, font=font(9), anchor="lm", fill=tc)
    if text_right:
        ac = accent if accent else color
        d.text((x+w-8,y), text_right, font=font(9,bold=True),
               anchor="rm", fill=(*ac, int(220*opacity)))
    composite(img_pil, layer)

# ─── Scene 0: Icons isolated ──────────────────────────────────────────────────
def scene00(f, img):
    for i, name in enumerate(ALL_ICONS):
        op = lerp_e(f, i*5, i*5+18)
        cx,cy = icon_px(name)
        float_y = int(math.sin(f*0.06 + i*0.9)*6)
        draw_icon(img, name, cx, cy+float_y, opacity=op)
    d = ImageDraw.Draw(img)
    text_c(d, "Viele Betriebe. Viele Tools. Kein Überblick.",
           H-55, opacity=lerp_e(f,25,50), size=14)

# ─── Scene 1: Chaos ───────────────────────────────────────────────────────────
def scene01(f, img):
    for i,name in enumerate(ALL_ICONS):
        cx,cy = icon_px(name)
        float_y = int(math.sin(f*0.06+i*0.9)*5)
        draw_icon(img, name, cx, cy+float_y)
    for i,(a,b) in enumerate(CONNECTIONS):
        p = lerp_e(f, i*5, i*5+28)
        draw_line(img, *icon_px(a), *icon_px(b), progress=p,
                  color=LINE_COLORS[i], width=1, opacity=0.60)
    d = ImageDraw.Draw(img)
    text_c(d, "Jedes Tool erfüllt seine Aufgabe — aber zusammenarbeiten tun sie selten.",
           H-55, opacity=lerp_e(f,90,115), size=13)

# ─── Scene 2: Freeze ──────────────────────────────────────────────────────────
def scene02(f, img):
    scale = lerp_e(f, 0, 55, 1.0, 0.84)
    sub = Image.fromarray(make_background())
    for i,name in enumerate(ALL_ICONS):
        cx,cy = icon_px(name)
        float_y = int(math.sin(f*0.05+i*0.9)*3) if f<55 else 0
        draw_icon(sub, name, cx, cy+float_y)
    for i,(a,b) in enumerate(CONNECTIONS):
        draw_line(sub, *icon_px(a), *icon_px(b), progress=1.0,
                  color=LINE_COLORS[i], width=1, opacity=0.50)
    nw,nh = int(W*scale), int(H*scale)
    sub_s = sub.resize((nw,nh), Image.LANCZOS)
    img.paste(sub_s, ((W-nw)//2, (H-nh)//2))
    d = ImageDraw.Draw(img)
    text_c(d, "Daten wandern. Informationen gehen verloren. Stunden verschwinden.",
           H-55, opacity=lerp_e(f,10,35), size=13)

# ─── Scene 3: Node emerges ────────────────────────────────────────────────────
def scene03(f, img):
    icon_op = lerp_e(f, 0, 40, 1.0, 0.20)
    line_op = lerp_e(f, 0, 28, 0.50, 0.0)
    node_sc = spring(f, 20)
    node_op = lerp_e(f, 20, 42)
    ord_op  = lerp_e(f, 48, 75)
    for i,(a,b) in enumerate(CONNECTIONS[:6]):
        draw_line(img, *icon_px(a), *icon_px(b), progress=1.0,
                  color=LINE_COLORS[i], width=1, opacity=line_op)
    if ord_op > 0:
        for i,name in enumerate(ALL_ICONS):
            cx2,cy2 = icon_px(name)
            p = lerp_e(f, 52+i*2, 78+i*2)
            draw_line(img, CENTER_PX[0], CENTER_PX[1], cx2, cy2,
                      progress=p, color=CYAN, width=1, opacity=ord_op*0.55)
    for i,name in enumerate(ALL_ICONS):
        cx,cy = icon_px(name)
        draw_icon(img, name, cx, cy, opacity=icon_op)
    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1],
                   scale=node_sc, opacity=node_op,
                   pulse=lerp_e(f,38,68))
    d = ImageDraw.Draw(img)
    text_c(d, "Was wäre, wenn alles in einer Plattform zusammenkommt?",
           H-55, opacity=lerp_e(f,90,115), size=14)

# ─── Scene 4: Integration dissolve ───────────────────────────────────────────
def scene04(f, img):
    others = [n for n in ALL_ICONS if n != "Craftnote"]
    for name in others:
        draw_line(img, CENTER_PX[0],CENTER_PX[1], *icon_px(name),
                  progress=1.0, color=CYAN, width=1, opacity=0.40)
    draw_glow_node(img, CENTER_PX[0],CENTER_PX[1], scale=1.0, opacity=1.0)
    for name in others:
        draw_icon(img, name, *icon_px(name), opacity=0.55)
    drift = lerp_e(f, 0, 44)
    orig  = icon_px("Craftnote")
    cx    = int(orig[0]+(CENTER_PX[0]-orig[0])*drift)
    cy    = int(orig[1]+(CENTER_PX[1]-orig[1])*drift)
    icon_op = lerp_e(f, 44, 60, 1.0, 0.0)
    bub_op  = lerp_e(f, 18, 38)
    if bub_op > 0:
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        br = int(lerp(f,36,54,45,70))
        dd.ellipse([cx-br,cy-br,cx+br,cy+br],
                   fill=None, outline=(*CYAN,int(125*bub_op)), width=2)
        composite(img, layer)
    pp = lerp_e(f, 50, 86)
    if pp > 0:
        draw_particles(img, CENTER_PX[0],CENTER_PX[1], pp, color=AMBER)
    draw_icon(img, "Craftnote", cx, cy, opacity=icon_op)
    d = ImageDraw.Draw(img)
    text_c(d, "Ein System, das alle Tools integriert — oder sogar ersetzt.",
           H-55, opacity=lerp_e(f,100,125), size=13)

# ─── Scene 5: Dashboard UI (NEW) ─────────────────────────────────────────────
def scene05_dashboard(f, img):
    """Animated mock of the real platform dashboard."""
    bg_op    = lerp_e(f, 0, 18)
    panel_op = lerp_e(f, 12, 38)
    cards_op = lerp_e(f, 30, 58)
    kpi_op   = lerp_e(f, 52, 80)
    sub_op   = lerp_e(f, 70, 100)

    # Ambient center glow
    layer = new_layer()
    dd = ImageDraw.Draw(layer)
    for r,a in [(380,12),(240,18),(140,25)]:
        dd.ellipse([CENTER_PX[0]-r, CENTER_PX[1]-r,
                    CENTER_PX[0]+r, CENTER_PX[1]+r],
                   fill=(*BLUE, int(a*bg_op)))
    composite(img, layer)

    # Sidebar mock
    sidebar_x = 100
    draw_ui_panel(img, sidebar_x, 80, 155, 520,
                  "PROJEKTPLATTFORM", opacity=panel_op*0.7, accent=CYAN)
    if panel_op > 0.1:
        layer2 = new_layer()
        dd2 = ImageDraw.Draw(layer2)
        items = ["Dashboard", "Projekte", "Mitarbeiter",
                 "Plantafel", "Reklamationen", "Zeiterfassung", "Archiv"]
        for i, it in enumerate(items):
            iy = 128 + i * 64
            is_active = (i == 0)
            if is_active:
                dd2.rounded_rectangle([sidebar_x+8, iy-12, sidebar_x+147, iy+12],
                                       radius=5, fill=(*CYAN, int(35*panel_op)))
            base_c = WHITE if is_active else GRAY
            tc = (*base_c, int(200*panel_op))
            dd2.text((sidebar_x+20, iy), it, font=font(10, bold=is_active),
                     anchor="lm", fill=tc)
        composite(img, layer2)

    # Main area title
    main_x = 280
    if cards_op > 0:
        d = ImageDraw.Draw(img)
        d.text((main_x + 10, 60), "Dashboard", font=font(22, bold=True),
               anchor="lm", fill=(*WHITE, int(235*cards_op)))
        d.text((main_x + 10, 88), "Letzte 7 Tage  ·  Alle Projekte",
               font=font(10), anchor="lm", fill=(*GRAY, int(170*cards_op)))

    # Card 1: Meine Projekte
    if cards_op > 0:
        px0,py0 = main_x, 115
        draw_ui_panel(img, px0, py0, 380, 160, "Meine Projekte",
                      opacity=cards_op, accent=CYAN)
        layer3 = new_layer()
        dd3 = ImageDraw.Draw(layer3)
        projs = [
            ("Dachsanierung Müller",   "IN ABARBEITUNG", BLUE),
            ("Heizung Schmidt",         "ANGEBOT AUSSTEHEND", AMBER),
            ("Fenster Bauer GmbH",      "FERTIGGESTELLT", GREEN),
        ]
        for i,(pname,status,sc) in enumerate(projs):
            ry = py0+46+i*36
            dd3.text((px0+12, ry), pname, font=font(10),
                     anchor="lm", fill=(*LGRAY, int(190*cards_op)))
            # status chip
            tw = font(8).getlength(status)+8
            dd3.rounded_rectangle([px0+370-tw, ry-8, px0+370, ry+8],
                                   radius=3, fill=(*sc, int(50*cards_op)),
                                   outline=(*sc, int(100*cards_op)), width=1)
            dd3.text((px0+370-tw//2, ry), status, font=font(8),
                     anchor="mm", fill=(*sc, int(200*cards_op)))
        composite(img, layer3)

    # Card 2: Akut / Risiken
    if cards_op > 0:
        rx0,ry0 = main_x+400, 115
        draw_ui_panel(img, rx0, ry0, 310, 160, "Akut / Risiken",
                      opacity=cards_op, accent=RED)
        layer4 = new_layer()
        dd4 = ImageDraw.Draw(layer4)
        risks = [
            ("Überfällige Projekte", "0", GREEN),
            ("Material überfällig",  "1", AMBER),
            ("Offene Tickets",        "3", RED),
        ]
        for i,(rname,rval,rc) in enumerate(risks):
            rry = ry0+46+i*36
            dd4.text((rx0+12, rry), rname, font=font(10),
                     anchor="lm", fill=(*LGRAY, int(185*cards_op)))
            dd4.rounded_rectangle([rx0+280, rry-12, rx0+308, rry+12],
                                   radius=12, fill=(*rc, int(45*cards_op)))
            dd4.text((rx0+294, rry), rval, font=font(11,bold=True),
                     anchor="mm", fill=(*rc, int(230*cards_op)))
        composite(img, layer4)

    # KPI row
    if kpi_op > 0:
        kx0 = main_x
        draw_ui_panel(img, kx0, 296, 710, 90, "Letzte Aktivitäten",
                      opacity=kpi_op, accent=CYAN)
        layer5 = new_layer()
        dd5 = ImageDraw.Draw(layer5)
        acts = [
            "Schmidt — Status → IN ABARBEITUNG",
            "Dachsanierung Müller — Dokument hochgeladen",
            "Heizung Bauer — E-Mail Ticket erstellt",
        ]
        for i,act in enumerate(acts):
            ay = 328+i*22
            dd5.text((kx0+12, ay), act, font=font(9),
                     anchor="lm", fill=(*GRAY, int(175*kpi_op)))
        composite(img, layer5)

    # Heuteplan card
    if sub_op > 0:
        draw_ui_panel(img, main_x, 406, 710, 80,
                      "Heuteplan — laufende Baustellen",
                      opacity=sub_op, accent=TEAL)
        layer6 = new_layer()
        dd6 = ImageDraw.Draw(layer6)
        bs = ["Dachsanierung Müller  –  3 Mitarbeiter",
              "Heizung Schmidt  –  Beginn 09:00"]
        for i,b in enumerate(bs):
            dd6.text((main_x+12, 432+i*22), b, font=font(9),
                     anchor="lm", fill=(*LGRAY, int(180*sub_op)))
        composite(img, layer6)

    d = ImageDraw.Draw(img)
    text_c(d, "Dein Betrieb auf einen Blick — immer aktuell.",
           H-55, opacity=lerp_e(f, 130, 160), size=14, color=WHITE)

# ─── Scene 6: Kanban Pipeline (NEW) ──────────────────────────────────────────
KANBAN_COLS = [
    ("INTERESSENT",        "33", (100,130,200)),
    ("ANGEBOT AUSSTEHEND", "10", AMBER),
    ("IN ABARBEITUNG",     "4",  BLUE),
    ("FERTIGGESTELLT",     "5",  GREEN),
]
KANBAN_CARDS = [
    # (name, start_col, end_col, anim_start)
    ("Dachsanierung Müller",  0, 2, 35),
    ("Heizung Schmidt",       0, 1, 55),
    ("Fenster Bauer GmbH",    1, 3, 70),
    ("Rohrbau Meier",         2, 2,  0),
    ("Abdichtung Krämer",     0, 0,  0),
    ("WaWi? Schneider",       1, 1,  0),
]

def scene06_kanban(f, img):
    """Animated Kanban pipeline board."""
    title_op = lerp_e(f, 0, 20)
    cols_op   = lerp_e(f, 8, 35)
    cards_op  = lerp_e(f, 28, 58)
    move_p    = lerp_e(f, 40, 100)

    # Title
    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Projektübersicht", font=font(22,bold=True),
               anchor="mm", fill=(*WHITE, int(235*title_op)))
        d.text((W//2, 72), "Von der Anfrage bis zur Fertigstellung — jeder Schritt sichtbar.",
               font=font(11), anchor="mm", fill=(*GRAY, int(170*title_op)))

    col_w  = 270
    col_h  = 490
    col_gap = 24
    board_x = (W - (col_w*4 + col_gap*3))//2
    board_y = 100

    col_x_list = [board_x + i*(col_w+col_gap) for i in range(4)]

    for ci,(cname,ccount,ccolor) in enumerate(KANBAN_COLS):
        cx0 = col_x_list[ci]
        op  = lerp_e(f, ci*6+8, ci*6+28) * cols_op
        if op <= 0: continue
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        # Column bg
        dd.rounded_rectangle([cx0, board_y, cx0+col_w, board_y+col_h],
                              radius=8, fill=(10,12,28,int(180*op)))
        # Header
        dd.rounded_rectangle([cx0, board_y, cx0+col_w, board_y+38],
                              radius=8, fill=(*ccolor, int(40*op)))
        dd.rounded_rectangle([cx0, board_y+28, cx0+col_w, board_y+38],
                              radius=0, fill=(*ccolor, int(40*op)))
        dd.text((cx0+12, board_y+18), cname, font=font(10,bold=True),
                anchor="lm", fill=(*WHITE, int(215*op)))
        # Count badge
        bw = 28
        dd.rounded_rectangle([cx0+col_w-bw-6, board_y+7, cx0+col_w-6, board_y+30],
                              radius=10, fill=(*ccolor, int(60*op)))
        dd.text((cx0+col_w-bw//2-6, board_y+18), ccount, font=font(10,bold=True),
                anchor="mm", fill=(*WHITE, int(230*op)))
        composite(img, layer)

    # Static background cards
    static_cards = [
        (0, "Rohrbau Meier",     (100,130,200)),
        (0, "Abdichtung Krämer", (80,110,170)),
        (1, "WaWi? Schneider",   AMBER),
        (2, "Projekt CN-XX",     BLUE),
        (3, "Projekt abg. 1",    GREEN),
        (3, "Projekt abg. 2",    (50,170,100)),
    ]
    if cards_op > 0.05:
        for ci,cname,ccolor in static_cards:
            cx0 = col_x_list[ci]
            op  = cards_op * lerp_e(f, ci*6+28, ci*6+48)
            layer = new_layer()
            dd   = ImageDraw.Draw(layer)
            cy0  = board_y + 50 + (static_cards.index((ci,cname,ccolor)) % 3) * 72
            dd.rounded_rectangle([cx0+8, cy0, cx0+col_w-8, cy0+58],
                                  radius=6, fill=(*ccolor, int(15*op)),
                                  outline=(*ccolor, int(55*op)), width=1)
            dd.text((cx0+16, cy0+28), cname, font=font(10),
                    anchor="lm", fill=(*LGRAY, int(195*op)))
            composite(img, layer)

    # Animated moving card: "Dachsanierung Müller" col 0 → col 2
    if move_p > 0 and cards_op > 0.1:
        src_cx = col_x_list[0]
        dst_cx = col_x_list[2]
        t_move = clamp(move_p)
        cx0    = int(src_cx + (dst_cx - src_cx) * ease_in_out(t_move))
        cy0    = board_y + 120
        op_m   = lerp_e(f, 30, 50) * min(1.0, lerp_e(f, 115, 150, 1.0, 0.0))
        if op_m > 0:
            layer = new_layer()
            dd    = ImageDraw.Draw(layer)
            dd.rounded_rectangle([cx0+8, cy0, cx0+col_w-8, cy0+58],
                                  radius=6, fill=(*CYAN, int(22*op_m)),
                                  outline=(*CYAN, int(100*op_m)), width=2)
            dd.text((cx0+16, cy0+20), "Dachsanierung Müller", font=font(10,bold=True),
                    anchor="lm", fill=(*WHITE, int(220*op_m)))
            draw_status_badge(img, cx0+16, cy0+42,
                              "IN ABARBEITUNG", BLUE, opacity=op_m)
            composite(img, layer)

    d = ImageDraw.Draw(img)
    text_c(d, "Von der Anfrage bis zur Fertigstellung — kein Auftrag geht verloren.",
           H-55, opacity=lerp_e(f, 145, 175), size=13, color=WHITE)

# ─── Scene 7: Zeiterfassung Live (NEW) ───────────────────────────────────────
def scene07_zeit(f, img):
    """Live timer + stats — Zeiterfassung."""
    title_op = lerp_e(f, 0, 20)
    panel_op = lerp_e(f, 12, 38)
    stats_op = lerp_e(f, 35, 60)
    timer_op = lerp_e(f, 22, 48)

    # Title
    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Zeiterfassung", font=font(22,bold=True),
               anchor="mm", fill=(*WHITE, int(235*title_op)))
        d.text((W//2, 72), "Wer arbeitet wo — und wie produktiv.",
               font=font(11), anchor="mm", fill=(*GRAY, int(165*title_op)))

    # Live timer panel (center)
    tp_x, tp_y, tp_w, tp_h = 340, 100, 600, 110
    draw_ui_panel(img, tp_x, tp_y, tp_w, tp_h, "Laufende Stempeluhr",
                  opacity=panel_op, accent=CYAN)

    if timer_op > 0:
        # Animated seconds counter
        seconds = int(f * 1.8) % 3600
        h_t     = seconds // 3600
        m_t     = (seconds % 3600) // 60
        s_t     = seconds % 60
        timer_str = f"{h_t:02d}:{m_t:02d}:{s_t:02d}"
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        # Glow behind timer
        for gr,ga in [(80,15),(55,25),(30,40)]:
            dd.ellipse([W//2-gr, tp_y+54-gr//2, W//2+gr, tp_y+54+gr//2],
                       fill=(*CYAN, int(ga*timer_op)))
        dd.text((W//2, tp_y+54), timer_str, font=font(36,bold=True),
                anchor="mm", fill=(*CYAN, int(245*timer_op)))
        dd.text((W//2, tp_y+88), "● LIVE — 2 Mitarbeiter aktiv",
                font=font(10), anchor="mm",
                fill=(*GREEN, int(200*timer_op)))
        composite(img, layer)

    # Stats row
    stat_defs = [
        ("6.50 h",   "Stunden",      WHITE),
        ("4",        "Einträge",      LGRAY),
        ("2",        "Live",         GREEN),
        ("4.10 h",   "Produktiv",     CYAN),
        ("2.40 h",   "Unproduktiv",   AMBER),
        ("63.1 %",   "Produktivität", BLUE),
    ]
    if stats_op > 0:
        sw  = 170
        sgap = 20
        total_w = len(stat_defs)*sw + (len(stat_defs)-1)*sgap
        sx0 = (W - total_w)//2
        sy0 = 238
        for i,(val,lbl,col) in enumerate(stat_defs):
            bx = sx0 + i*(sw+sgap)
            op_i = lerp_e(f, 38+i*5, 58+i*5) * stats_op
            draw_ui_panel(img, bx, sy0, sw, 68, "", opacity=op_i*0.7, accent=col)
            if op_i > 0.05:
                draw_ui_stat(img, bx+sw//2, sy0+30, val, lbl,
                             opacity=op_i, color=col, vsize=20)

    # Employee active rows
    emp_op = lerp_e(f, 72, 100) * stats_op
    if emp_op > 0.05:
        ex0, ey0 = 200, 336
        draw_ui_panel(img, ex0, ey0, 880, 108,
                      "Aktive Mitarbeiter", opacity=emp_op, accent=GREEN)
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        employees = [
            ("Thomas K.",   "Dachsanierung Müller",    "seit  07:45", GREEN),
            ("Sandra M.",   "Bestellübersicht Büro",   "seit  08:12", CYAN),
        ]
        for i,(name,proj,seit,ec) in enumerate(employees):
            ry = ey0+48+i*30
            # dot
            dd.ellipse([ex0+12, ry-5, ex0+22, ry+5], fill=(*ec, int(220*emp_op)))
            dd.text((ex0+32, ry), name, font=font(10,bold=True),
                    anchor="lm", fill=(*WHITE, int(215*emp_op)))
            dd.text((ex0+160, ry), proj, font=font(10),
                    anchor="lm", fill=(*GRAY, int(180*emp_op)))
            dd.text((ex0+860, ry), seit, font=font(9),
                    anchor="rm", fill=(*ec, int(195*emp_op)))
        composite(img, layer)

    d = ImageDraw.Draw(img)
    text_c(d, "Arbeitszeiten, Produktivität und Urlaub — alles in einer Ansicht.",
           H-55, opacity=lerp_e(f, 130, 158), size=13, color=WHITE)

# ─── Scene 8: Ticketsystem (NEW) ─────────────────────────────────────────────
def scene08_tickets(f, img):
    """E-Mail → Ticket automation."""
    title_op = lerp_e(f, 0, 20)
    arrow_op = lerp_e(f, 18, 45)
    list_op  = lerp_e(f, 45, 72)
    deep_op  = lerp_e(f, 70, 100)

    # Title
    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Ticketsystem", font=font(22,bold=True),
               anchor="mm", fill=(*WHITE, int(235*title_op)))

    # E-Mail icon → Arrow → Ticket
    email_cx, email_cy = 310, 200
    ticket_cx, ticket_cy = 720, 200
    arrow_mid  = 515

    if arrow_op > 0:
        # Email box
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        # Email icon
        for gr,ga in [(55,18),(38,30),(22,48)]:
            dd.ellipse([email_cx-gr,email_cy-gr,email_cx+gr,email_cy+gr],
                       fill=(156,39,176, int(ga*arrow_op)))
        dd.rounded_rectangle([email_cx-40,email_cy-28,email_cx+40,email_cy+28],
                              radius=8, fill=(156,39,176,int(30*arrow_op)),
                              outline=(156,39,176,int(120*arrow_op)), width=2)
        dd.text((email_cx, email_cy), "✉", font=font(22),
                anchor="mm", fill=(*WHITE, int(230*arrow_op)))
        dd.text((email_cx, email_cy+44), "E-Mail Eingang",
                font=font(10), anchor="mm",
                fill=(*GRAY, int(190*arrow_op)))
        # Arrow line
        p_arr = lerp_e(f, 25, 52)
        arr_x = int(email_cx+45 + (ticket_cx-45 - email_cx-45)*p_arr)
        dd.line([(email_cx+45, email_cy), (arr_x, email_cy)],
                fill=(*CYAN, int(200*arrow_op)), width=2)
        if p_arr > 0.9:
            dd.polygon([
                (arr_x, email_cy-8),
                (arr_x+14, email_cy),
                (arr_x, email_cy+8)],
                fill=(*CYAN, int(200*arrow_op)))
        # Label above arrow
        if p_arr > 0.5:
            dd.text((arrow_mid, email_cy-22), "→  automatisch",
                    font=font(9), anchor="mm",
                    fill=(*CYAN, int(170*arrow_op*(p_arr-0.5)*2)))
        composite(img, layer)

        if p_arr > 0.85:
            # Ticket box
            layer2 = new_layer()
            dd2 = ImageDraw.Draw(layer2)
            t_op  = lerp_e(f, 40, 60)
            for gr,ga in [(55,18),(38,28),(22,45)]:
                dd2.ellipse([ticket_cx-gr,ticket_cy-gr,
                             ticket_cx+gr,ticket_cy+gr],
                            fill=(*CYAN, int(ga*t_op)))
            dd2.rounded_rectangle([ticket_cx-55,ticket_cy-38,
                                   ticket_cx+55,ticket_cy+38],
                                  radius=8, fill=(*CYAN, int(22*t_op)),
                                  outline=(*CYAN, int(110*t_op)), width=2)
            dd2.text((ticket_cx, ticket_cy-8), "TKT-2026", font=font(12,bold=True),
                     anchor="mm", fill=(*WHITE, int(230*t_op)))
            dd2.text((ticket_cx, ticket_cy+12), "Neues Ticket",
                     font=font(9), anchor="mm",
                     fill=(*LGRAY, int(180*t_op)))
            draw_status_badge(img, ticket_cx-20, ticket_cy+32,
                              "offen", AMBER, opacity=t_op)
            composite(img, layer2)

    # Ticket list
    if list_op > 0.05:
        lx0, ly0 = 140, 280
        draw_ui_panel(img, lx0, ly0, 1000, 200, "Ticketsystem — Übersicht",
                      opacity=list_op, accent=CYAN)
        layer3 = new_layer()
        dd3 = ImageDraw.Draw(layer3)
        tickets = [
            ("TKT-2026-0075", "Re: ISOTEC Angebot AN-091-26-02",  "offen", "mittel", "E-Mail Eingang"),
            ("TKT-2026-0074", "WG: Halteverbotszone",              "offen", "mittel", "E-Mail Eingang"),
            ("TKT-2026-0073", "Anfrage Abdichtung Ottsen",         "offen", "niedrig","E-Mail Eingang"),
            ("TKT-2026-0072", "ISOTEC-Schadensanalyse Reinz",      "offen", "niedrig","E-Mail Eingang"),
        ]
        # header
        for xi,hd in [(lx0+12,"Ticket"), (lx0+155,"Betreff"),
                      (lx0+590,"Status"), (lx0+700,"Priorität"),
                      (lx0+830,"Quelle")]:
            dd3.text((xi, ly0+46), hd, font=font(9,bold=True),
                     anchor="lm", fill=(*CYAN, int(160*list_op)))
        for i,(tid,sbj,st,pri,qll) in enumerate(tickets):
            ry = ly0+68+i*32
            op_r = lerp_e(f, 52+i*6, 70+i*6) * list_op
            if op_r <= 0: continue
            dd3.rounded_rectangle([lx0+6, ry-10, lx0+994, ry+12],
                                   radius=3, fill=(255,255,255,int(6*op_r)))
            dd3.text((lx0+12, ry), tid, font=font(9,bold=True),
                     anchor="lm", fill=(*CYAN, int(200*op_r)))
            dd3.text((lx0+155, ry), sbj, font=font(9),
                     anchor="lm", fill=(*LGRAY, int(190*op_r)))
            sc_st = RED if st=="offen" else GREEN
            dd3.text((lx0+590, ry), st, font=font(9),
                     anchor="lm", fill=(*sc_st, int(205*op_r)))
            sc_pr = AMBER if pri=="mittel" else GRAY
            dd3.text((lx0+700, ry), pri, font=font(9),
                     anchor="lm", fill=(*sc_pr, int(200*op_r)))
            dd3.text((lx0+830, ry), qll, font=font(9),
                     anchor="lm", fill=(*GRAY, int(175*op_r)))
        composite(img, layer3)

    d = ImageDraw.Draw(img)
    text_c(d, "Jede E-Mail wird automatisch zum Ticket. Keine Anfrage geht verloren.",
           H-55, opacity=lerp_e(f, 110, 140), size=13, color=WHITE)

# ─── Scene 9: Dokumente & Archiv (NEW) ───────────────────────────────────────
def scene09_dokumente(f, img):
    """Document management module — folder structure, search, file open."""
    title_op  = lerp_e(f, 0, 22)
    panel_op  = lerp_e(f, 15, 42)
    tree_op   = lerp_e(f, 35, 68)
    search_op = lerp_e(f, 75, 105)
    file_op   = lerp_e(f, 110, 140)

    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Dokumente & Archiv", font=font(22, bold=True),
               anchor="mm", fill=(*WHITE, int(235 * title_op)))
        d.text((W//2, 72), "Alle Unterlagen. Immer griffbereit.",
               font=font(11), anchor="mm", fill=(*GRAY, int(165 * title_op)))

    # Left: folder tree panel
    lx0, ly0 = 100, 100
    draw_ui_panel(img, lx0, ly0, 300, 420, "Ordnerstruktur",
                  opacity=panel_op, accent=AMBER)

    if tree_op > 0:
        folders = [
            ("📁 Baupläne",      0, AMBER),
            ("  📄 Müller.pdf",  1, LGRAY),
            ("  📄 Schmidt.pdf", 1, LGRAY),
            ("📁 Verträge",      0, AMBER),
            ("  📄 Rahmenvertrag.pdf", 1, LGRAY),
            ("📁 Fotos",         0, AMBER),
            ("📁 Angebote",      0, AMBER),
            ("  📄 AN-091-26.pdf", 1, LGRAY),
        ]
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        for i, (name, indent, col) in enumerate(folders):
            fy = ly0 + 48 + i * 42
            op_f = lerp_e(f, 38 + i * 5, 58 + i * 5) * tree_op
            if op_f <= 0:
                continue
            is_folder = name.startswith("📁")
            if is_folder:
                dd.rounded_rectangle([lx0 + 8, fy - 12, lx0 + 292, fy + 12],
                                     radius=4, fill=(*AMBER, int(12 * op_f)))
            dd.text((lx0 + 16 + indent * 18, fy), name, font=font(10),
                    anchor="lm", fill=(*col, int(200 * op_f)))
        composite(img, layer)

    # Right: file detail / search panel
    rx0, ry0 = 430, 100
    draw_ui_panel(img, rx0, ry0, 750, 80, "Suche",
                  opacity=search_op, accent=CYAN)

    if search_op > 0:
        layer2 = new_layer()
        dd2 = ImageDraw.Draw(layer2)
        # Search bar
        dd2.rounded_rectangle([rx0 + 12, ry0 + 36, rx0 + 738, ry0 + 64],
                               radius=6, fill=(30, 35, 60, int(200 * search_op)),
                               outline=(*CYAN, int(80 * search_op)), width=1)
        # Animated cursor typing "Müller"
        query = "Müller"
        shown = query[:max(0, int(lerp_e(f, 82, 118) * len(query)))]
        cursor = "|" if (f // 15) % 2 == 0 else ""
        dd2.text((rx0 + 22, ry0 + 50), f"🔍  {shown}{cursor}",
                 font=font(11), anchor="lm",
                 fill=(*WHITE, int(220 * search_op)))
        composite(img, layer2)

    # Results
    if file_op > 0:
        draw_ui_panel(img, rx0, ry0 + 100, 750, 310, "Suchergebnisse — 3 Treffer",
                      opacity=file_op, accent=AMBER)
        layer3 = new_layer()
        dd3 = ImageDraw.Draw(layer3)
        results = [
            ("Müller.pdf",          "Baupläne",  "2.4 MB", "15.02.2026"),
            ("Müller_Angebot.pdf",  "Angebote",  "0.8 MB", "03.01.2026"),
            ("Müller_Fotos.zip",    "Fotos",     "48 MB",  "10.03.2026"),
        ]
        headers = ["Dateiname", "Ordner", "Größe", "Datum"]
        header_xs = [rx0 + 12, rx0 + 320, rx0 + 530, rx0 + 640]
        for xi, hd in zip(header_xs, headers):
            dd3.text((xi, ry0 + 146), hd, font=font(9, bold=True),
                     anchor="lm", fill=(*AMBER, int(150 * file_op)))
        for i, (fname, folder, size, date) in enumerate(results):
            ry = ry0 + 168 + i * 64
            op_r = lerp_e(f, 118 + i * 8, 140 + i * 8) * file_op
            if op_r <= 0:
                continue
            dd3.rounded_rectangle([rx0 + 6, ry - 16, rx0 + 744, ry + 26],
                                   radius=4, fill=(255, 255, 255, int(7 * op_r)))
            dd3.text((rx0 + 12, ry), fname, font=font(10, bold=True),
                     anchor="lm", fill=(*LGRAY, int(210 * op_r)))
            dd3.text((rx0 + 320, ry), folder, font=font(10),
                     anchor="lm", fill=(*AMBER, int(180 * op_r)))
            dd3.text((rx0 + 530, ry), size, font=font(9),
                     anchor="lm", fill=(*GRAY, int(170 * op_r)))
            dd3.text((rx0 + 640, ry), date, font=font(9),
                     anchor="lm", fill=(*GRAY, int(170 * op_r)))
        composite(img, layer3)

    d = ImageDraw.Draw(img)
    text_c(d, "Alle Unterlagen. Immer griffbereit — vom Büro oder der Baustelle.",
           H - 55, opacity=lerp_e(f, 138, 165), size=13, color=WHITE)


# ─── Scene 10: Kalkulation / BLS-Import (NEW) ────────────────────────────────
def scene10_kalkulation(f, img):
    """BLS icon glows, data streams into calculation panel, positions build up."""
    title_op  = lerp_e(f, 0, 22)
    icon_op   = lerp_e(f, 10, 35)
    stream_p  = lerp_e(f, 28, 65)
    table_op  = lerp_e(f, 60, 90)
    total_op  = lerp_e(f, 110, 140)

    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Kalkulation", font=font(22, bold=True),
               anchor="mm", fill=(*WHITE, int(235 * title_op)))
        d.text((W//2, 72), "Direkt aus dem BLS — ohne doppelte Dateneingabe.",
               font=font(11), anchor="mm", fill=(*GRAY, int(165 * title_op)))

    bls_cx, bls_cy = 220, 360
    panel_x, panel_y = 430, 120

    # BLS icon
    if icon_op > 0:
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        for gr, ga in [(62, 16), (44, 26), (26, 44)]:
            dd.ellipse([bls_cx - gr, bls_cy - gr, bls_cx + gr, bls_cy + gr],
                       fill=(*ORANGE, int(ga * icon_op)))
        dd.rounded_rectangle([bls_cx - 44, bls_cy - 32, bls_cx + 44, bls_cy + 32],
                              radius=10, fill=(*ORANGE, int(28 * icon_op)),
                              outline=(*ORANGE, int(120 * icon_op)), width=2)
        dd.text((bls_cx, bls_cy - 6), "BLS", font=font(20, bold=True),
                anchor="mm", fill=(*WHITE, int(230 * icon_op)))
        dd.text((bls_cx, bls_cy + 50), "BLS Import", font=font(10),
                anchor="mm", fill=(*GRAY, int(180 * icon_op)))
        composite(img, layer)

    # Stream line
    draw_line(img, bls_cx + 48, bls_cy, panel_x, panel_y + 250,
              progress=stream_p, color=ORANGE, width=2, opacity=0.85)

    # Kalkulation panel
    draw_ui_panel(img, panel_x, panel_y, 740, 440, "Kalkulation — Projekt Dachsanierung Müller",
                  opacity=table_op, accent=ORANGE)

    if table_op > 0:
        layer2 = new_layer()
        dd2 = ImageDraw.Draw(layer2)
        headers = ["Pos.", "Bezeichnung", "Einh.", "Menge", "EP €", "GP €"]
        hxs = [panel_x + 12, panel_x + 65, panel_x + 440, panel_x + 510,
                panel_x + 580, panel_x + 665]
        for xi, hd in zip(hxs, headers):
            dd2.text((xi, panel_y + 46), hd, font=font(9, bold=True),
                     anchor="lm", fill=(*ORANGE, int(150 * table_op)))

        positions = [
            ("1.", "Abdichtungsarbeiten Keller",  "m²",  "45",  "32,00",  "1.440,00"),
            ("2.", "Bitumenbahn zweilagig",        "m²",  "45",  "18,50",    "832,50"),
            ("3.", "Drainage verlegen",            "lfm", "28",  "24,00",    "672,00"),
            ("4.", "Schutzschicht aufbringen",     "m²",  "45",   "8,00",    "360,00"),
            ("5.", "Auffüllen & Verdichten",       "m³",  "12",  "62,00",    "744,00"),
        ]
        for i, (pos, bez, einh, mge, ep, gp) in enumerate(positions):
            ry = panel_y + 68 + i * 52
            op_r = lerp_e(f, 65 + i * 8, 88 + i * 8) * table_op
            if op_r <= 0:
                continue
            dd2.rounded_rectangle([panel_x + 6, ry - 14, panel_x + 734, ry + 18],
                                   radius=3, fill=(255, 255, 255, int(6 * op_r)))
            for xi, val in zip(hxs, [pos, bez, einh, mge, ep, gp]):
                bold = (val == gp)
                col = AMBER if bold else LGRAY
                dd2.text((xi, ry), val, font=font(10, bold=bold),
                         anchor="lm", fill=(*col, int(205 * op_r)))
        composite(img, layer2)

    # Animated total counter
    if total_op > 0:
        target = 4048.5
        current = lerp_e(f, 112, 148) * target
        layer3 = new_layer()
        dd3 = ImageDraw.Draw(layer3)
        dd3.line([(panel_x + 6, panel_y + 342), (panel_x + 734, panel_y + 342)],
                 fill=(*ORANGE, int(60 * total_op)), width=1)
        dd3.text((panel_x + 12, panel_y + 368), "Gesamtnetto:",
                 font=font(13), anchor="lm",
                 fill=(*LGRAY, int(200 * total_op)))
        dd3.text((panel_x + 728, panel_y + 368), f"{current:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."),
                 font=font(16, bold=True), anchor="rm",
                 fill=(*AMBER, int(235 * total_op)))
        composite(img, layer3)

    d = ImageDraw.Draw(img)
    text_c(d, "Kalkulationen direkt aus dem BLS — kein Export, kein Abtippen.",
           H - 55, opacity=lerp_e(f, 130, 158), size=13, color=WHITE)


# ─── Scene 11: Buchhaltung / BMD-Sync (NEW) ──────────────────────────────────
def scene11_buchhaltung(f, img):
    """BMD icon glows, invoice list builds up, sync arrow pulses."""
    title_op = lerp_e(f, 0, 22)
    icon_op  = lerp_e(f, 10, 35)
    list_op  = lerp_e(f, 42, 72)
    sync_op  = lerp_e(f, 90, 118)

    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Buchhaltung & BMD-Sync", font=font(22, bold=True),
               anchor="mm", fill=(*WHITE, int(235 * title_op)))
        d.text((W//2, 72), "Rechnungen fließen automatisch — kein Export, kein Fehler.",
               font=font(11), anchor="mm", fill=(*GRAY, int(165 * title_op)))

    bmd_cx, bmd_cy = 220, 350
    bmd_color = (229, 57, 53)

    if icon_op > 0:
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        for gr, ga in [(62, 16), (44, 26), (26, 44)]:
            dd.ellipse([bmd_cx - gr, bmd_cy - gr, bmd_cx + gr, bmd_cy + gr],
                       fill=(*bmd_color, int(ga * icon_op)))
        dd.rounded_rectangle([bmd_cx - 44, bmd_cy - 32, bmd_cx + 44, bmd_cy + 32],
                              radius=10, fill=(*bmd_color, int(28 * icon_op)),
                              outline=(*bmd_color, int(120 * icon_op)), width=2)
        dd.text((bmd_cx, bmd_cy - 6), "BMD", font=font(20, bold=True),
                anchor="mm", fill=(*WHITE, int(230 * icon_op)))
        dd.text((bmd_cx, bmd_cy + 50), "Buchhaltung", font=font(10),
                anchor="mm", fill=(*GRAY, int(180 * icon_op)))
        composite(img, layer)

    # Invoice panel
    px, py = 430, 100
    draw_ui_panel(img, px, py, 750, 380, "Rechnungen", opacity=list_op, accent=bmd_color)

    if list_op > 0:
        layer2 = new_layer()
        dd2 = ImageDraw.Draw(layer2)
        headers = ["Rechnungs-Nr.", "Kunde", "Betrag", "Status", "BMD"]
        hxs = [px + 12, px + 180, px + 440, px + 570, px + 680]
        for xi, hd in zip(hxs, headers):
            dd2.text((xi, py + 46), hd, font=font(9, bold=True),
                     anchor="lm", fill=(*bmd_color, int(150 * list_op)))
        invoices = [
            ("RG-2026-0042", "ISOTEC Franchise GmbH",  "3.840,00 €", "bezahlt",    "✓"),
            ("RG-2026-0041", "Dachbau Müller",          "1.260,00 €", "offen",      "✓"),
            ("RG-2026-0040", "Schmidt Haustechnik",     "  890,00 €", "bezahlt",    "✓"),
            ("RG-2026-0039", "Fenster Bauer GmbH",      "2.100,00 €", "überfällig", "✓"),
        ]
        for i, (nr, kunde, betrag, status, bmd) in enumerate(invoices):
            ry = py + 68 + i * 68
            op_r = lerp_e(f, 48 + i * 8, 70 + i * 8) * list_op
            if op_r <= 0:
                continue
            dd2.rounded_rectangle([px + 6, ry - 14, px + 744, ry + 22],
                                   radius=3, fill=(255, 255, 255, int(6 * op_r)))
            dd2.text((px + 12, ry), nr, font=font(10, bold=True),
                     anchor="lm", fill=(*CYAN, int(210 * op_r)))
            dd2.text((px + 180, ry), kunde, font=font(10),
                     anchor="lm", fill=(*LGRAY, int(200 * op_r)))
            dd2.text((px + 440, ry), betrag, font=font(10, bold=True),
                     anchor="lm", fill=(*WHITE, int(215 * op_r)))
            sc = GREEN if status == "bezahlt" else (RED if status == "überfällig" else AMBER)
            dd2.text((px + 570, ry), status, font=font(9),
                     anchor="lm", fill=(*sc, int(210 * op_r)))
            dd2.text((px + 680, ry), bmd, font=font(12, bold=True),
                     anchor="lm", fill=(*GREEN, int(225 * op_r)))
        composite(img, layer2)

    # Sync arrow + badge
    if sync_op > 0:
        pulse = 0.5 + 0.5 * math.sin(f * 0.25)
        arr_op = sync_op * (0.7 + 0.3 * pulse)
        draw_line(img, bmd_cx + 48, bmd_cy - 20, px, py + 190,
                  progress=1.0, color=bmd_color, width=2, opacity=arr_op * 0.8)
        layer3 = new_layer()
        dd3 = ImageDraw.Draw(layer3)
        bw = 200
        bx0 = bmd_cx - bw // 2
        by0 = bmd_cy + 80
        dd3.rounded_rectangle([bx0, by0, bx0 + bw, by0 + 32], radius=6,
                               fill=(*GREEN, int(30 * sync_op)),
                               outline=(*GREEN, int(100 * sync_op)), width=1)
        dd3.text((bmd_cx, by0 + 16), "✓  Synchronisiert",
                 font=font(11, bold=True), anchor="mm",
                 fill=(*GREEN, int(225 * sync_op)))
        composite(img, layer3)

    d = ImageDraw.Draw(img)
    text_c(d, "Rechnungen fließen automatisch in die Buchhaltung.",
           H - 55, opacity=lerp_e(f, 120, 148), size=13, color=WHITE)


# ─── Scene 12: Mobile / Baustelle (NEW) ──────────────────────────────────────
def scene12_mobile(f, img):
    """Desktop dashboard left, smartphone mockup right, sync arrow between."""
    title_op  = lerp_e(f, 0, 22)
    desk_op   = lerp_e(f, 15, 48)
    phone_op  = lerp_e(f, 50, 80)
    sync_op   = lerp_e(f, 78, 108)
    loc_op    = lerp_e(f, 110, 138)

    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Im Büro. Auf der Baustelle.", font=font(22, bold=True),
               anchor="mm", fill=(*WHITE, int(235 * title_op)))
        d.text((W//2, 72), "Immer dieselbe Plattform — überall verfügbar.",
               font=font(11), anchor="mm", fill=(*GRAY, int(165 * title_op)))

    # Desktop panel (left side)
    dx, dy = 60, 110
    draw_ui_panel(img, dx, dy, 490, 460, "Dashboard — Desktop",
                  opacity=desk_op, accent=CYAN)
    if desk_op > 0:
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        desk_items = [
            ("Meine Projekte",    "5 aktiv",   CYAN),
            ("Offene Tickets",    "3 offen",   AMBER),
            ("Zeiterfassung",     "2 live",    GREEN),
            ("Letzte Aktivität",  "vor 2 Min", LGRAY),
            ("Heuteplan",         "3 Baustellen", BLUE),
        ]
        for i, (label, val, col) in enumerate(desk_items):
            ry = dy + 52 + i * 72
            op_i = lerp_e(f, 22 + i * 6, 45 + i * 6) * desk_op
            if op_i <= 0:
                continue
            dd.rounded_rectangle([dx + 10, ry - 16, dx + 480, ry + 28],
                                  radius=5, fill=(*col, int(12 * op_i)))
            dd.text((dx + 20, ry), label, font=font(11),
                    anchor="lm", fill=(*LGRAY, int(200 * op_i)))
            dd.text((dx + 470, ry), val, font=font(11, bold=True),
                    anchor="rm", fill=(*col, int(225 * op_i)))
        composite(img, layer)

    # Smartphone silhouette (right side)
    ph_cx, ph_cy = 950, 360
    ph_w, ph_h = 200, 360
    ph_x0, ph_y0 = ph_cx - ph_w // 2, ph_cy - ph_h // 2

    if phone_op > 0:
        layer2 = new_layer()
        dd2 = ImageDraw.Draw(layer2)
        # Phone body
        dd2.rounded_rectangle([ph_x0, ph_y0, ph_x0 + ph_w, ph_y0 + ph_h],
                               radius=24, fill=(15, 18, 40, int(220 * phone_op)),
                               outline=(*CYAN, int(90 * phone_op)), width=2)
        # Notch
        dd2.rounded_rectangle([ph_cx - 30, ph_y0 + 6, ph_cx + 30, ph_y0 + 18],
                               radius=6, fill=(5, 6, 20, int(200 * phone_op)))
        # Home bar
        dd2.rounded_rectangle([ph_cx - 30, ph_y0 + ph_h - 12, ph_cx + 30, ph_y0 + ph_h - 6],
                               radius=4, fill=(*GRAY, int(100 * phone_op)))
        # Mini UI inside phone
        phone_items = [
            ("Projekte", "5", CYAN),
            ("Tickets",  "3", AMBER),
            ("Zeit",     "●", GREEN),
            ("Dokumente","↑", BLUE),
        ]
        for i, (lbl, val, col) in enumerate(phone_items):
            iy = ph_y0 + 42 + i * 62
            op_p = lerp_e(f, 56 + i * 5, 78 + i * 5) * phone_op
            if op_p <= 0:
                continue
            dd2.rounded_rectangle([ph_x0 + 8, iy, ph_x0 + ph_w - 8, iy + 48],
                                   radius=6, fill=(*col, int(18 * op_p)))
            dd2.text((ph_cx, iy + 16), val, font=font(14, bold=True),
                     anchor="mm", fill=(*col, int(230 * op_p)))
            dd2.text((ph_cx, iy + 34), lbl, font=font(9),
                     anchor="mm", fill=(*GRAY, int(185 * op_p)))
        composite(img, layer2)

    # Bidirectional sync arrows
    if sync_op > 0:
        pulse = 0.5 + 0.5 * math.sin(f * 0.22)
        arr_op = sync_op * (0.6 + 0.4 * pulse)
        mx = (dx + 490 + ph_x0) // 2
        draw_line(img, dx + 490, dy + 230, ph_x0, ph_cy,
                  progress=lerp_e(f, 80, 110), color=CYAN, width=2, opacity=arr_op)
        draw_line(img, ph_x0, ph_cy + 40, dx + 490, dy + 260,
                  progress=lerp_e(f, 88, 118), color=CYAN, width=2, opacity=arr_op * 0.7)
        if sync_op > 0.5:
            d = ImageDraw.Draw(img)
            d.text((mx + 20, dy + 240), "SYNC", font=font(9, bold=True),
                   anchor="mm", fill=(*CYAN, int(180 * sync_op)))

    # Location pin
    if loc_op > 0:
        layer3 = new_layer()
        dd3 = ImageDraw.Draw(layer3)
        pin_x, pin_y = ph_cx, ph_y0 + ph_h + 30
        dd3.ellipse([pin_x - 6, pin_y - 6, pin_x + 6, pin_y + 6],
                    fill=(*GREEN, int(220 * loc_op)))
        dd3.text((pin_x + 12, pin_y), "Baustelle Müller — GPS aktiv",
                 font=font(10), anchor="lm",
                 fill=(*GREEN, int(200 * loc_op)))
        composite(img, layer3)

    d = ImageDraw.Draw(img)
    text_c(d, "Im Büro. Auf der Baustelle. Immer dieselbe Plattform.",
           H - 55, opacity=lerp_e(f, 140, 168), size=13, color=WHITE)


# ─── Scene 13: Warenwirtschaft ────────────────────────────────────────────────
def scene09_ware(f, img):
    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1], scale=0.65, opacity=0.55)
    od_pos  = icon_px("OneDrive")
    mod_pos = (int(W*0.72), H//2)
    stream_p = lerp_e(f, 5, 48)
    draw_line(img, od_pos[0],od_pos[1], mod_pos[0],mod_pos[1],
              progress=stream_p, color=CYAN, width=2, opacity=0.9)
    draw_line(img, od_pos[0],od_pos[1], CENTER_PX[0],CENTER_PX[1],
              progress=1.0, color=BLUE, width=1, opacity=0.32)
    draw_icon(img, "OneDrive", od_pos[0],od_pos[1], glowing=True)
    mod_op = lerp_e(f, 44, 64)
    draw_module_card(img, mod_pos[0],mod_pos[1], "Warenwirtschaft",
                     ["Artikel & Material", "Lagerbestände",
                      "Bestellübersicht", "Liefertermine"],
                     opacity=mod_op, color=CYAN, w=215)
    d = ImageDraw.Draw(img)
    text_c(d, "Material wird automatisch organisiert und nachverfolgt.",
           H-55, opacity=lerp_e(f,52,70), size=14)

# ─── Scene 10: Projektverwaltung ─────────────────────────────────────────────
def scene10_proj(f, img):
    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1], scale=0.5, opacity=0.42)
    ware_pos = (int(W*0.30), int(H*0.40))
    proj_pos = (int(W*0.66), int(H*0.40))
    time_pos = (int(W*0.66), int(H*0.72))
    conn_p = lerp_e(f, 18, 55)
    draw_line(img, ware_pos[0]+105,ware_pos[1],
              proj_pos[0]-105,proj_pos[1],
              progress=conn_p, color=CYAN, width=2)
    t2_p = lerp_e(f, 50, 75)
    draw_line(img, proj_pos[0],proj_pos[1]+60,
              time_pos[0],time_pos[1]-55,
              progress=t2_p, color=PURPLE, width=1)
    draw_module_card(img, ware_pos[0],ware_pos[1], "Warenwirtschaft",
                     ["Artikel & Material","Lagerbestände"],
                     opacity=lerp_e(f,0,18), color=CYAN, w=200)
    draw_module_card(img, proj_pos[0],proj_pos[1], "Projektverwaltung",
                     ["Kanban & Aufgaben","Fortschritt","Ressourcen","Meilensteine"],
                     opacity=lerp_e(f,48,68), color=(0,220,200), w=220)
    draw_module_card(img, time_pos[0],time_pos[1], "Zeiterfassung",
                     ["Arbeitszeiten","Auswertungen"],
                     opacity=lerp_e(f,58,76), color=PURPLE, w=200)
    d = ImageDraw.Draw(img)
    text_c(d, "Projekte, Aufgaben und Zeiten — strukturiert auf einen Blick.",
           H-55, opacity=lerp_e(f,56,74), size=14)

# ─── Scene 11: Social Proof — ISOTEC / VITERMA (NEW) ─────────────────────────
ISOTEC_MODULES = [
    "Auswertung Arbeitszeit",
    "Bestellformular",
    "Bestellübersicht",
    "Lagerbestandsführung",
    "Ticketsystem",
    "Rechnungen",
    "Aufgaben",
]
VITERMA_MODULES = [
    "Bestellformular",
    "MediaPlan",
    "Projektverwaltung",
    "Rechnungen",
    "Warenwirtschaft",
    "Aufgaben",
]

def scene11_social(f, img):
    """Split screen: ISOTEC vs. VITERMA — each has their own module set."""
    title_op  = lerp_e(f, 0, 22)
    left_op   = lerp_e(f, 14, 42)
    right_op  = lerp_e(f, 28, 58)
    badge_op  = lerp_e(f, 55, 85)
    sub_op    = lerp_e(f, 140, 168)

    # Divider line center
    if title_op > 0:
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        dd.line([(W//2, 80), (W//2, H-80)],
                fill=(*CYAN, int(40*title_op)), width=1)
        composite(img, layer)

    # Title
    if title_op > 0:
        d = ImageDraw.Draw(img)
        d.text((W//2, 45), "Individuell konfiguriert. Für jeden Betrieb.",
               font=font(20,bold=True), anchor="mm",
               fill=(*WHITE, int(235*title_op)))

    card_w = 520
    card_h = 440

    # Left panel: ISOTEC
    if left_op > 0:
        lx0, ly0 = 60, 88
        draw_ui_panel(img, lx0, ly0, card_w, card_h,
                      "ISOTEC  ·  7 Module", opacity=left_op, accent=RED)
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        # Logo text
        dd.text((lx0+12, ly0+48), "ISOTEC", font=font(28,bold=True),
                anchor="lm", fill=(*RED, int(220*left_op)))
        dd.text((lx0+12, ly0+80), "IMMER BESSER.",
                font=font(10), anchor="lm",
                fill=(*GRAY, int(150*left_op)))
        dd.line([(lx0+12, ly0+98),(lx0+card_w-12, ly0+98)],
                fill=(*RED, int(40*left_op)), width=1)
        for i,mod in enumerate(ISOTEC_MODULES):
            my = ly0+118+i*45
            op_m = lerp_e(f, 18+i*4, 36+i*4) * left_op
            dd.rounded_rectangle([lx0+12, my-14, lx0+card_w-12, my+14],
                                  radius=5, fill=(*RED, int(14*op_m)))
            dd.ellipse([lx0+20, my-5, lx0+30, my+5],
                       fill=(*RED, int(180*op_m)))
            dd.text((lx0+40, my), mod, font=font(11),
                    anchor="lm", fill=(*LGRAY, int(200*op_m)))
            # Live badge
            dd.rounded_rectangle([lx0+card_w-60, my-9, lx0+card_w-12, my+9],
                                  radius=8, fill=(*GREEN, int(35*op_m)))
            dd.text((lx0+card_w-36, my), "Live", font=font(9,bold=True),
                    anchor="mm", fill=(*GREEN, int(210*op_m)))
        composite(img, layer)

    # Right panel: VITERMA (dark theme)
    if right_op > 0:
        rx0, ry0 = W - card_w - 60, 88
        draw_ui_panel(img, rx0, ry0, card_w, card_h,
                      "VITERMA  ·  6 Module", opacity=right_op, accent=TEAL)
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        dd.text((rx0+12, ry0+48), "VITERMA", font=font(28,bold=True),
                anchor="lm", fill=(*TEAL, int(220*right_op)))
        dd.text((rx0+12, ry0+80), "Unternehmenssteuerung.",
                font=font(10), anchor="lm",
                fill=(*GRAY, int(150*right_op)))
        dd.line([(rx0+12, ry0+98),(rx0+card_w-12, ry0+98)],
                fill=(*TEAL, int(40*right_op)), width=1)
        for i,mod in enumerate(VITERMA_MODULES):
            my = ry0+118+i*53
            op_m = lerp_e(f, 30+i*4, 50+i*4) * right_op
            dd.rounded_rectangle([rx0+12, my-14, rx0+card_w-12, my+14],
                                  radius=5, fill=(*TEAL, int(14*op_m)))
            dd.ellipse([rx0+20, my-5, rx0+30, my+5],
                       fill=(*TEAL, int(180*op_m)))
            dd.text((rx0+40, my), mod, font=font(11),
                    anchor="lm", fill=(*LGRAY, int(200*op_m)))
            dd.rounded_rectangle([rx0+card_w-60, my-9, rx0+card_w-12, my+9],
                                  radius=8, fill=(*TEAL, int(35*op_m)))
            dd.text((rx0+card_w-36, my), "Live", font=font(9,bold=True),
                    anchor="mm", fill=(*TEAL, int(210*op_m)))
        composite(img, layer)

    # Sub-text
    d = ImageDraw.Draw(img)
    text_c(d, "Jede Plattform wird individuell konfiguriert — genau für deinen Betrieb.",
           H-55, opacity=sub_op, size=13, color=WHITE)

# ─── Scene 16: Kundenzitat (NEW) ─────────────────────────────────────────────
def scene16_quote(f, img):
    """Customer quote — animated line-by-line reveal."""
    bg_op    = lerp_e(f, 0, 25)
    mark_op  = lerp_e(f, 8, 30)
    line1_op = lerp_e(f, 22, 48)
    line2_op = lerp_e(f, 50, 75)
    name_op  = lerp_e(f, 90, 115)
    bar_op   = lerp_e(f, 5, 28)

    # Ambient glow
    if bg_op > 0:
        layer = new_layer()
        dd = ImageDraw.Draw(layer)
        for r, a in [(320, 12), (200, 20), (100, 30)]:
            dd.ellipse([CENTER_PX[0] - r, CENTER_PX[1] - r,
                        CENTER_PX[0] + r, CENTER_PX[1] + r],
                       fill=(*BLUE, int(a * bg_op)))
        composite(img, layer)

    # Accent bar
    if bar_op > 0:
        lw = int(lerp_e(f, 5, 28) * 280)
        d = ImageDraw.Draw(img)
        d.line([(CENTER_PX[0] - lw, CENTER_PX[1] - 120),
                (CENTER_PX[0] + lw, CENTER_PX[1] - 120)],
               fill=(*CYAN, int(90 * bar_op)), width=1)

    # Quotation marks
    if mark_op > 0:
        layer2 = new_layer()
        dd2 = ImageDraw.Draw(layer2)
        dd2.text((CENTER_PX[0] - 260, CENTER_PX[1] - 105),
                 "\u201e", font=font(72, bold=True),
                 anchor="lm", fill=(*CYAN, int(80 * mark_op)))
        composite(img, layer2)

    # Quote lines
    d = ImageDraw.Draw(img)
    if line1_op > 0:
        d.text((CENTER_PX[0], CENTER_PX[1] - 50),
               "Endlich sehen wir alles auf einen Blick.",
               font=font(26), anchor="mm",
               fill=(*WHITE, int(240 * line1_op)))
    if line2_op > 0:
        d.text((CENTER_PX[0], CENTER_PX[1] + 10),
               "Unsere Projektleiter sparen täglich zwei Stunden.",
               font=font(26), anchor="mm",
               fill=(*WHITE, int(240 * line2_op)))

    # Name + company
    if name_op > 0:
        layer3 = new_layer()
        dd3 = ImageDraw.Draw(layer3)
        # Avatar circle
        av_x, av_y = CENTER_PX[0] - 180, CENTER_PX[1] + 88
        dd3.ellipse([av_x - 22, av_y - 22, av_x + 22, av_y + 22],
                    fill=(*CYAN, int(40 * name_op)),
                    outline=(*CYAN, int(100 * name_op)), width=1)
        dd3.text((av_x, av_y), "MR", font=font(14, bold=True),
                 anchor="mm", fill=(*CYAN, int(220 * name_op)))
        dd3.text((av_x + 36, av_y - 8), "Michael R.",
                 font=font(13, bold=True), anchor="lm",
                 fill=(*WHITE, int(220 * name_op)))
        dd3.text((av_x + 36, av_y + 10), "Geschäftsführer — ISOTEC Franchise",
                 font=font(10), anchor="lm",
                 fill=(*GRAY, int(180 * name_op)))
        composite(img, layer3)

    # Stars
    if name_op > 0.3:
        layer4 = new_layer()
        dd4 = ImageDraw.Draw(layer4)
        for si in range(5):
            dd4.text((CENTER_PX[0] + 40 + si * 26, CENTER_PX[1] + 88),
                     "★", font=font(16),
                     anchor="mm", fill=(*AMBER, int(220 * name_op)))
        composite(img, layer4)


# ─── Scene 17: Full overview ──────────────────────────────────────────────────
DASH_MODULES = [
    {"pos":(0.20,0.28),"title":"Projekte",     "items":["Kanban","Aufgaben"],          "color":CYAN,           "w":165},
    {"pos":(0.38,0.28),"title":"Material",     "items":["Bestände","Bestellungen"],    "color":(0,220,200),    "w":165},
    {"pos":(0.56,0.28),"title":"Kommunikation","items":["E-Mails","Tickets"],          "color":PURPLE,         "w":165},
    {"pos":(0.74,0.28),"title":"Dokumente",    "items":["Dateien","Verträge"],         "color":(255,152,0),    "w":165},
    {"pos":(0.20,0.68),"title":"Buchhaltung",  "items":["Rechnungen","BMD-Sync"],     "color":(229,57,53),    "w":165},
    {"pos":(0.38,0.68),"title":"Kalkulation",  "items":["BLS-Import","Positionen"],   "color":ORANGE,         "w":165},
    {"pos":(0.56,0.68),"title":"Zeiterfassung","items":["Arbeitszeiten","Auswertung"],"color":(76,175,80),    "w":165},
    {"pos":(0.74,0.68),"title":"Berichte",     "items":["KPIs","Auswertungen"],       "color":(0,188,212),    "w":165},
]

def scene12_overview(f, img):
    scale = lerp_e(f, 0, 55, 1.12, 1.0)
    sub   = Image.fromarray(make_background())
    draw_glow_node(sub, CENTER_PX[0],CENTER_PX[1], scale=0.42, opacity=0.30)
    for i,m in enumerate(DASH_MODULES):
        mx = int(m["pos"][0]*W)
        my = int(m["pos"][1]*H)
        mo = lerp_e(f, i*4, i*4+22)
        draw_line(sub, CENTER_PX[0],CENTER_PX[1], mx,my,
                  progress=1.0, color=m["color"], width=1, opacity=mo*0.22)
        draw_module_card(sub, mx,my, m["title"],m["items"],
                         opacity=mo, color=m["color"], w=m["w"])
    nw,nh = int(W*scale),int(H*scale)
    sub_s = sub.resize((nw,nh), Image.LANCZOS)
    img.paste(sub_s, ((W-nw)//2,(H-nh)//2))
    d = ImageDraw.Draw(img)
    text_c(d, "Aus vielen Programmen wird eine Plattform.",
           H-55, opacity=lerp_e(f,62,82), size=14)

# ─── Scene 18: Finale ─────────────────────────────────────────────────────────
def scene13_finale(f, img):
    # Ambient glow
    glow_a = int((0.28 + math.sin(f*0.12)*0.09) * 200)
    layer  = new_layer()
    dd     = ImageDraw.Draw(layer)
    for r,a in [(380,int(glow_a*0.08)),(260,int(glow_a*0.14)),(150,int(glow_a*0.22))]:
        dd.ellipse([CENTER_PX[0]-r,CENTER_PX[1]-r,
                    CENTER_PX[0]+r,CENTER_PX[1]+r],
                   fill=(*BLUE, a))
    composite(img, layer)

    # Horizontal accent lines
    line_op = lerp_e(f, 5, 25)
    if line_op > 0:
        d = ImageDraw.Draw(img)
        lw = int(lerp_e(f,5,25)*350)
        if lw > 0:
            d.line([(CENTER_PX[0]-lw, CENTER_PX[1]-65),
                    (CENTER_PX[0]+lw, CENTER_PX[1]-65)],
                   fill=(*CYAN, int(100*line_op)), width=1)
            d.line([(CENTER_PX[0]-lw//2, CENTER_PX[1]+95),
                    (CENTER_PX[0]+lw//2, CENTER_PX[1]+95)],
                   fill=(*CYAN, int(60*line_op)), width=1)

    # Line 1
    op1 = lerp_e(f, 10, 32)
    # Line 2
    op2 = lerp_e(f, 32, 56)
    # Subtitle
    op3 = lerp_e(f, 56, 75)
    # CTA
    op4 = lerp_e(f, 80, 100)

    d = ImageDraw.Draw(img)
    d.text((CENTER_PX[0], CENTER_PX[1]-22), "Ein Betriebssystem",
           font=font(54), anchor="mm",
           fill=(*WHITE, int(op1*248)))
    d.text((CENTER_PX[0], CENTER_PX[1]+48), "für deinen Betrieb.",
           font=font(54,bold=True), anchor="mm",
           fill=(*CYAN, int(op2*248)))
    text_c(d, "Übersichtlich  ·  Strukturiert  ·  Individuell konfiguriert",
           CENTER_PX[1]+105, opacity=op3, size=15, color=LGRAY)

    # CTA pill button
    if op4 > 0.05:
        layer2 = new_layer()
        dd2    = ImageDraw.Draw(layer2)
        bw,bh  = 280, 42
        bx0    = CENTER_PX[0]-bw//2
        by0    = CENTER_PX[1]+148
        dd2.rounded_rectangle([bx0,by0,bx0+bw,by0+bh], radius=21,
                               fill=(*CYAN, int(35*op4)),
                               outline=(*CYAN, int(120*op4)), width=2)
        dd2.text((CENTER_PX[0], by0+bh//2), "Jetzt entdecken →",
                 font=font(14,bold=True), anchor="mm",
                 fill=(*WHITE, int(235*op4)))
        composite(img, layer2)

    # Fade to black
    fade = lerp_e(f, 190, 218)
    if fade > 0:
        overlay = Image.new("RGB",(W,H),(0,0,0))
        mask    = Image.fromarray(np.full((H,W),int(fade*255),dtype=np.uint8))
        img.paste(overlay, mask=mask)

# ─── Scene 19: Logo Outro (NEW) ──────────────────────────────────────────────
def scene19_outro(f, img):
    """Final branded outro — glow node + logo text + fade to black."""
    glow_op  = lerp_e(f, 0, 30)
    logo_op  = lerp_e(f, 25, 55)
    claim_op = lerp_e(f, 48, 75)
    fade_out = lerp_e(f, 85, 112)

    if glow_op > 0:
        pulse = 0.5 + 0.5 * math.sin(f * 0.18)
        draw_glow_node(img, CENTER_PX[0], CENTER_PX[1],
                       scale=1.2 + 0.1 * pulse, opacity=glow_op * 0.85,
                       pulse=pulse)

    d = ImageDraw.Draw(img)
    if logo_op > 0:
        d.text((CENTER_PX[0], CENTER_PX[1] - 30),
               "Projektplattform",
               font=font(48, bold=True), anchor="mm",
               fill=(*CYAN, int(245 * logo_op)))
    if claim_op > 0:
        d.text((CENTER_PX[0], CENTER_PX[1] + 32),
               "Das Betriebssystem für dein Handwerk.",
               font=font(16), anchor="mm",
               fill=(*LGRAY, int(210 * claim_op)))

    if fade_out > 0:
        overlay = Image.new("RGB", (W, H), (0, 0, 0))
        mask = Image.fromarray(np.full((H, W), int(fade_out * 255), dtype=np.uint8))
        img.paste(overlay, mask=mask)


# ─── Scene dispatch ───────────────────────────────────────────────────────────
SCENE_FNS = [
    scene00,              # 0  — Icons isoliert
    scene01,              # 1  — Chaos-Linien
    scene02,              # 2  — Freeze
    scene03,              # 3  — Node entsteht
    scene04,              # 4  — Integration dissolve
    scene05_dashboard,    # 5  — Dashboard UI
    scene06_kanban,       # 6  — Kanban Pipeline
    scene07_zeit,         # 7  — Zeiterfassung
    scene08_tickets,      # 8  — Ticketsystem
    scene09_dokumente,    # 9  — Dokumente & Archiv     (NEU)
    scene10_kalkulation,  # 10 — Kalkulation / BLS      (NEU)
    scene11_buchhaltung,  # 11 — Buchhaltung / BMD      (NEU)
    scene12_mobile,       # 12 — Mobile / Baustelle     (NEU)
    scene09_ware,         # 13 — Warenwirtschaft
    scene10_proj,         # 14 — Projektverwaltung
    scene11_social,       # 15 — Social Proof ISOTEC/VITERMA
    scene16_quote,        # 16 — Kundenzitat            (NEU)
    scene12_overview,     # 17 — Komplettübersicht
    scene13_finale,       # 18 — Finale Tagline
    scene19_outro,        # 19 — Logo Outro             (NEU)
]

def render_frame(global_frame: int) -> np.ndarray:
    # Find scene
    scene_idx = 0
    for i,start in enumerate(SCENE_STARTS):
        if global_frame >= start:
            scene_idx = i
    local_frame = global_frame - SCENE_STARTS[scene_idx]
    bg  = make_background()
    img = Image.fromarray(bg)
    SCENE_FNS[scene_idx](local_frame, img)
    return np.array(img)

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"ffmpeg: {ffmpeg_path}")
    duration = TOTAL_FRAMES / FPS
    print(f"Rendering {TOTAL_FRAMES} frames @ {W}×{H} {FPS}fps  →  {duration:.1f}s")
    print(f"Output: {OUT_PATH}\n")

    writer = imageio.get_writer(
        OUT_PATH, fps=FPS, codec="libx264", quality=None,
        ffmpeg_params=["-crf","18","-preset","fast","-pix_fmt","yuv420p"],
        ffmpeg_log_level="warning",
    )

    for f in range(TOTAL_FRAMES):
        frame = render_frame(f)
        writer.append_data(frame)
        if f % 30 == 0:
            # Find scene name
            si = 0
            for i,s in enumerate(SCENE_STARTS):
                if f >= s: si = i
            print(f"  {f/TOTAL_FRAMES*100:5.1f}%  frame {f:4d}/{TOTAL_FRAMES}"
                  f"  Szene {si+1}/{len(SCENE_FNS)}", flush=True)

    writer.close()
    size_mb = os.path.getsize(OUT_PATH)/1024/1024
    print(f"\nFertig! → {OUT_PATH}  ({size_mb:.1f} MB, {duration:.1f}s)")

if __name__ == "__main__":
    main()
