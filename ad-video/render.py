"""
Handwerk Ad Video Renderer — Python/PIL/NumPy + imageio-ffmpeg
30 seconds @ 30fps = 900 frames @ 1280x720
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
import math
import sys
import os

# ─── Config ──────────────────────────────────────────────────────────────────
W, H = 1280, 720
FPS = 30
TOTAL_FRAMES = 900  # 30s
OUT_PATH = os.path.join(os.path.dirname(__file__), "out", "ad-video.mp4")
os.makedirs(os.path.join(os.path.dirname(__file__), "out"), exist_ok=True)

# ─── Colors ───────────────────────────────────────────────────────────────────
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
CYAN        = (0, 200, 255)
BLUE        = (0, 120, 255)
PURPLE      = (123, 79, 255)
GRAY        = (140, 150, 180)
DARK_BLUE   = (5, 5, 20)

# ─── Animation helpers ────────────────────────────────────────────────────────
def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def lerp(frame, f0, f1, v0=0.0, v1=1.0):
    if f1 == f0: return v1 if frame >= f1 else v0
    t = clamp((frame - f0) / (f1 - f0))
    return v0 + (v1 - v0) * t

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def lerp_ease(frame, f0, f1, v0=0.0, v1=1.0):
    t = clamp((frame - f0) / max(f1 - f0, 1))
    return v0 + (v1 - v0) * ease_in_out(t)

def spring(frame, start, stiffness=0.3, damping=0.7):
    """Simplified spring: returns 0→1 value"""
    t = max(0, frame - start) / FPS
    if t <= 0: return 0.0
    omega = math.sqrt(stiffness) * 15
    zeta = damping
    if zeta < 1:
        wd = omega * math.sqrt(1 - zeta ** 2)
        val = 1 - math.exp(-zeta * omega * t) * (
            math.cos(wd * t) + (zeta * omega / wd) * math.sin(wd * t)
        )
    else:
        val = 1 - math.exp(-omega * t) * (1 + omega * t)
    return clamp(val)

# ─── Icon layout (normalized → pixel) ────────────────────────────────────────
def px(nx, ny=None):
    if ny is None: return int(nx * W)
    return int(nx * W), int(ny * H)

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
CENTER_N = (0.50, 0.50)

def icon_px(name):
    nx, ny = ICON_NORM[name]
    return (int(nx * W), int(ny * H))

CENTER_PX = (W // 2, H // 2)

ICON_META = {
    "BLS":       {"color": (255, 107,  53), "emoji": "📊", "label": "BLS"},
    "BMD":       {"color": (229,  57,  53), "emoji": "📋", "label": "BMD"},
    "Sevdesk":   {"color": (  0, 188, 212), "emoji": "🧾", "label": "Sevdesk"},
    "Excel":     {"color": ( 33, 115,  70), "emoji": "📈", "label": "Excel"},
    "OneDrive":  {"color": (  0, 120, 212), "emoji": "☁",  "label": "OneDrive"},
    "Dropbox":   {"color": (  0,  97, 255), "emoji": "📦", "label": "Dropbox"},
    "Email":     {"color": (156,  39, 176), "emoji": "✉",  "label": "E-Mail"},
    "Craftnote": {"color": (255, 152,   0), "emoji": "🔨", "label": "Craftnote"},
}

# ─── Drawing helpers ───────────────────────────────────────────────────────────
def alpha_blend(base: np.ndarray, overlay: np.ndarray, alpha: float) -> np.ndarray:
    a = clamp(alpha)
    return (base * (1 - a) + overlay * a).astype(np.uint8)

def radial_gradient(w, h, cx, cy, r, inner_col, outer_col=(0,0,0)):
    """Returns RGBA numpy array with radial gradient"""
    x = np.arange(w)
    y = np.arange(h)
    xx, yy = np.meshgrid(x, y)
    dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
    t = np.clip(dist / r, 0, 1)
    img = np.zeros((h, w, 4), dtype=np.float32)
    for c in range(3):
        img[:,:,c] = inner_col[c] * (1 - t) + outer_col[c] * t
    img[:,:,3] = (1 - t) * 255
    return img.astype(np.uint8)

def make_background(frame=0):
    """Dark background with subtle blue-ish center glow"""
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:] = (3, 3, 15)  # very dark blue
    # radial vignette center lighter
    cx, cy = W//2, H//2
    x = np.arange(W)
    y = np.arange(H)
    xx, yy = np.meshgrid(x, y)
    dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
    glow = np.clip(1.0 - dist / (max(W,H) * 0.6), 0, 1) * 12
    img[:,:,0] = np.clip(img[:,:,0] + glow * 0.5, 0, 255).astype(np.uint8)
    img[:,:,1] = np.clip(img[:,:,1] + glow * 0.3, 0, 255).astype(np.uint8)
    img[:,:,2] = np.clip(img[:,:,2] + glow * 1.5, 0, 255).astype(np.uint8)
    return img

def draw_glow_circle(draw, cx, cy, r, color, layers=4):
    """Draw a glowing circle using multiple alpha layers"""
    for i in range(layers, 0, -1):
        factor = i / layers
        ar = r + (layers - i) * r * 0.5
        alpha_val = int(40 * factor)
        c = tuple(list(color) + [alpha_val])
        draw.ellipse([cx-ar, cy-ar, cx+ar, cy+ar],
                     fill=c, outline=None)

def draw_icon(img_pil: Image.Image, name: str, cx: int, cy: int,
              opacity: float = 1.0, scale: float = 1.0, glowing: bool = False):
    """Draw a software icon box at (cx,cy) with given opacity/scale"""
    if opacity <= 0.01: return
    size = int(70 * scale)
    half = size // 2
    meta = ICON_META[name]
    color = meta["color"]
    label = meta["label"]

    # Create icon on transparent layer
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Glow behind icon
    if glowing or opacity > 0.5:
        glow_r = half + 20
        for gi in range(4, 0, -1):
            ga = int(25 * gi / 4 * opacity)
            gr = glow_r + (4 - gi) * 10
            d.ellipse([cx-gr, cy-gr, cx+gr, cy+gr],
                      fill=(*color, ga))

    # Box background
    x0, y0 = cx - half, cy - half
    x1, y1 = cx + half, cy + half
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(14*scale),
                        fill=(*color, int(30*opacity)),
                        outline=(*color, int(120*opacity)),
                        width=2)

    # Accent dot
    dot_r = int(5 * scale)
    d.ellipse([x1-dot_r*2-2, y1-dot_r*2-2, x1-2, y1-2],
              fill=(*color, int(200*opacity)))

    # Label text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                  int(10 * scale))
    except:
        font = ImageFont.load_default()

    # Icon letter(s) in center
    try:
        big_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                       int(20 * scale))
    except:
        big_font = ImageFont.load_default()

    d.text((cx, cy - int(4*scale)), label[:2],
           font=big_font, anchor="mm",
           fill=(*WHITE, int(220*opacity)))

    # Label below
    d.text((cx, cy + half + int(10*scale)), label,
           font=font, anchor="mm",
           fill=(*GRAY, int(180*opacity)))

    # Composite
    img_alpha = img_pil.convert("RGBA")
    img_alpha = Image.alpha_composite(img_alpha, layer)
    img_pil.paste(img_alpha.convert("RGB"))

def draw_line(img_pil: Image.Image, x1, y1, x2, y2,
              progress=1.0, color=CYAN, width=2, opacity=1.0, curved=True):
    """Draw animated line from (x1,y1) toward (x2,y2) with progress 0-1"""
    if progress <= 0 or opacity <= 0.01: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Endpoint based on progress
    ex = int(x1 + (x2 - x1) * progress)
    ey = int(y1 + (y2 - y1) * progress)

    c = (*color, int(255 * opacity))
    cg = (*color, int(60 * opacity))  # glow

    # Glow (thicker, transparent)
    if opacity > 0.3:
        d.line([(x1, y1), (ex, ey)], fill=cg, width=width * 4)
    # Main line
    d.line([(x1, y1), (ex, ey)], fill=c, width=width)

    img_alpha = img_pil.convert("RGBA")
    img_alpha = Image.alpha_composite(img_alpha, layer)
    img_pil.paste(img_alpha.convert("RGB"))

def draw_text_center(draw: ImageDraw.ImageDraw, text: str, y: int,
                     opacity: float = 1.0, size: int = 16,
                     color=GRAY, bold=False):
    if opacity <= 0.01: return
    fname = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else \
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        font = ImageFont.truetype(fname, size)
    except:
        font = ImageFont.load_default()
    c = (*color, int(255 * opacity))
    draw.text((W//2, y), text, font=font, anchor="mm", fill=c)

def draw_module_card(img_pil: Image.Image, cx: int, cy: int,
                     title: str, items: list, opacity: float = 1.0,
                     color=CYAN, w=200, h=None):
    if opacity <= 0.01: return
    if h is None:
        h = 50 + len(items) * 22
    x0, y0 = cx - w//2, cy - h//2
    x1, y1 = cx + w//2, cy + h//2

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Card background
    d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                        fill=(10, 12, 30, int(210 * opacity)),
                        outline=(*color, int(100 * opacity)),
                        width=1)

    # Header bar
    d.rounded_rectangle([x0, y0, x1, y0+28], radius=10,
                        fill=(*color, int(40 * opacity)))
    d.rounded_rectangle([x0, y0+18, x1, y0+28], radius=0,
                        fill=(*color, int(40 * opacity)))

    # Accent dot
    d.ellipse([x0+8, y0+10, x0+18, y0+20],
              fill=(*color, int(220 * opacity)))

    try:
        font_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
        font_item = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        font_title = font_item = ImageFont.load_default()

    d.text((x0 + 24, y0 + 14), title, font=font_title, anchor="lm",
           fill=(*WHITE, int(230 * opacity)))

    for i, item in enumerate(items):
        iy = y0 + 38 + i * 20
        d.ellipse([x0+10, iy-3, x0+16, iy+3],
                  fill=(*color, int(150 * opacity)))
        d.text((x0+24, iy), item, font=font_item, anchor="lm",
               fill=(*GRAY, int(190 * opacity)))

    img_alpha = img_pil.convert("RGBA")
    img_alpha = Image.alpha_composite(img_alpha, layer)
    img_pil.paste(img_alpha.convert("RGB"))

def draw_glow_node(img_pil: Image.Image, cx: int, cy: int,
                   scale: float = 1.0, opacity: float = 1.0, pulse=0.0):
    if opacity <= 0.01 or scale <= 0.01: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Outer glow rings
    for ri, (r, a) in enumerate([(90, 20), (60, 35), (36, 55), (20, 80)]):
        r2 = int(r * scale)
        d.ellipse([cx-r2, cy-r2, cx+r2, cy+r2],
                  fill=(*BLUE, int(a * opacity)))

    # Pulse ring
    if pulse > 0:
        pr = int((24 + (90 - 24) * pulse) * scale)
        pa = int((1 - pulse) * 200 * opacity)
        d.ellipse([cx-pr, cy-pr, cx+pr, cy+pr],
                  fill=None, outline=(*CYAN, pa), width=2)

    # Core
    cr = int(20 * scale)
    d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr],
              fill=(*WHITE, int(240 * opacity)))
    # Inner dot
    dr = int(6 * scale)
    d.ellipse([cx-dr, cy-dr, cx+dr, cy+dr],
              fill=(*BLUE, int(200 * opacity)))

    img_alpha = img_pil.convert("RGBA")
    img_alpha = Image.alpha_composite(img_alpha, layer)
    img_pil.paste(img_alpha.convert("RGB"))

def draw_particles(img_pil: Image.Image, cx: int, cy: int, progress: float,
                   count=28, seed=42, color=(255,152,0)):
    if progress <= 0: return
    rng = np.random.default_rng(seed)
    angles = rng.uniform(0, 2*math.pi, count)
    speeds = rng.uniform(60, 180, count)
    sizes  = rng.uniform(2, 6, count)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(count):
        dist = speeds[i] * progress
        x = cx + int(math.cos(angles[i]) * dist)
        y = cy + int(math.sin(angles[i]) * dist)
        alpha = max(0, 1 - progress * 1.3)
        r = max(1, int(sizes[i] * (1 - progress * 0.6)))
        d.ellipse([x-r, y-r, x+r, y+r],
                  fill=(*color, int(alpha * 220)))

    img_alpha = img_pil.convert("RGBA")
    img_alpha = Image.alpha_composite(img_alpha, layer)
    img_pil.paste(img_alpha.convert("RGB"))

ALL_ICONS = list(ICON_META.keys())
CONNECTIONS = [
    ("Excel", "BMD"), ("Email", "Craftnote"),
    ("Dropbox", "BLS"), ("OneDrive", "Sevdesk"),
    ("BLS", "Craftnote"), ("BMD", "Email"),
    ("Sevdesk", "Excel"), ("OneDrive", "BMD"),
    ("Dropbox", "Email"), ("Excel", "Craftnote"),
    ("BLS", "Sevdesk"), ("Dropbox", "BMD"),
]
LINE_COLORS = [CYAN, BLUE, PURPLE, (255,107,53), (255,152,0),
               CYAN, BLUE, PURPLE, (0,188,212), CYAN, BLUE, PURPLE]

# ─── Scene renderers ──────────────────────────────────────────────────────────

def scene01(f, img):
    """Fragmentierte Softwarewelt: icons floating isolated"""
    d = ImageDraw.Draw(img.convert("RGBA"))
    draw = ImageDraw.Draw(img)
    for i, name in enumerate(ALL_ICONS):
        op = lerp_ease(f, i*5, i*5+15)
        cx, cy = icon_px(name)
        float_y = int(math.sin(f * 0.05 + i * 0.9) * 5)
        draw_icon(img, name, cx, cy + float_y, opacity=op)
    # subtitle
    op_text = lerp_ease(f, 15, 35)
    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Viele Handwerksbetriebe arbeiten mit einer Vielzahl einzelner Systeme.",
                     H - 55, opacity=op_text, size=14)

def scene02(f, img):
    """Komplexität: chaotic data lines"""
    for i, name in enumerate(ALL_ICONS):
        cx, cy = icon_px(name)
        float_y = int(math.sin(f * 0.05 + i * 0.9) * 4)
        draw_icon(img, name, cx, cy + float_y)
    for i, (a, b) in enumerate(CONNECTIONS):
        p = lerp_ease(f, i*5, i*5+25)
        x1, y1 = icon_px(a)
        x2, y2 = icon_px(b)
        draw_line(img, x1, y1, x2, y2, progress=p,
                  color=LINE_COLORS[i], width=1, opacity=0.65)
    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Jedes Tool erfüllt seine Aufgabe. Doch zusammenarbeiten tun sie selten.",
                     H - 55, opacity=lerp_ease(f, 60, 80), size=14)

def scene03(f, img):
    """Chaos sichtbar: zoom out + freeze"""
    # Already zoomed-out look: render slightly smaller scale
    scale = lerp_ease(f, 0, 55, 1.0, 0.84)

    # Create sub-image for scale effect
    sub = Image.fromarray(make_background())
    for i, name in enumerate(ALL_ICONS):
        cx, cy = icon_px(name)
        float_y = int(math.sin(f * 0.05 + i * 0.9) * 3) if f < 60 else 0
        draw_icon(sub, name, cx, cy + float_y)
    for i, (a, b) in enumerate(CONNECTIONS):
        x1, y1 = icon_px(a)
        x2, y2 = icon_px(b)
        draw_line(sub, x1, y1, x2, y2, progress=1.0,
                  color=LINE_COLORS[i], width=1, opacity=0.55)

    # Scale the sub-image
    new_w = int(W * scale)
    new_h = int(H * scale)
    sub_scaled = sub.resize((new_w, new_h), Image.LANCZOS)
    ox = (W - new_w) // 2
    oy = (H - new_h) // 2
    img.paste(sub_scaled, (ox, oy))

    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Daten wandern. Informationen gehen verloren.",
                     H - 55, opacity=lerp_ease(f, 5, 25), size=14)

def scene04(f, img):
    """Neues System entsteht: central glow node appears"""
    # Old icons fade out
    icon_op = lerp_ease(f, 0, 40, 1.0, 0.25)
    # Lines fade out
    line_op = lerp_ease(f, 0, 30, 0.5, 0.0)
    # Node scales in
    node_scale = spring(f, 20)
    node_op = lerp_ease(f, 20, 40)

    # Ordered lines from center to icons
    ord_op = lerp_ease(f, 45, 70)

    for i, (a, b) in enumerate(CONNECTIONS[:6]):
        x1, y1 = icon_px(a)
        x2, y2 = icon_px(b)
        draw_line(img, x1, y1, x2, y2, progress=1.0,
                  color=LINE_COLORS[i], width=1, opacity=line_op)

    # Ordered lines center → each icon
    if ord_op > 0:
        for i, name in enumerate(ALL_ICONS):
            cx2, cy2 = icon_px(name)
            p = lerp_ease(f, 50 + i*2, 75 + i*2)
            draw_line(img, CENTER_PX[0], CENTER_PX[1], cx2, cy2,
                      progress=p, color=CYAN, width=1, opacity=ord_op * 0.6)

    for i, name in enumerate(ALL_ICONS):
        cx, cy = icon_px(name)
        draw_icon(img, name, cx, cy, opacity=icon_op)

    pulse = lerp_ease(f, 35, 65)
    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1],
                   scale=node_scale, opacity=node_op, pulse=pulse)

    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Was wäre, wenn alles zusammenkommt?",
                     H - 55, opacity=lerp_ease(f, 55, 75), size=14)

def scene05(f, img):
    """Craftnote dissolve"""
    others = [n for n in ALL_ICONS if n != "Craftnote"]
    # Ordered lines center → icons
    for name in others:
        cx2, cy2 = icon_px(name)
        draw_line(img, CENTER_PX[0], CENTER_PX[1], cx2, cy2,
                  progress=1.0, color=CYAN, width=1, opacity=0.45)

    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1], scale=1.0, opacity=1.0)

    for i, name in enumerate(others):
        cx, cy = icon_px(name)
        draw_icon(img, name, cx, cy, opacity=0.6)

    # Craftnote drifts to center
    drift = lerp_ease(f, 0, 42)
    orig = icon_px("Craftnote")
    cx = int(orig[0] + (CENTER_PX[0] - orig[0]) * drift)
    cy = int(orig[1] + (CENTER_PX[1] - orig[1]) * drift)
    icon_op = lerp_ease(f, 42, 58, 1.0, 0.0)

    # Bubble
    bubble_op = lerp_ease(f, 18, 38)
    if bubble_op > 0:
        layer = Image.new("RGBA", (W, H), (0,0,0,0))
        d = ImageDraw.Draw(layer)
        br = int(lerp(f, 36, 52, 45, 70))
        d.ellipse([cx-br, cy-br, cx+br, cy+br],
                  fill=None, outline=(*CYAN, int(130*bubble_op)), width=2)
        img_a = img.convert("RGBA")
        img.paste(Image.alpha_composite(img_a, layer).convert("RGB"))

    # Particles
    p_prog = lerp_ease(f, 48, 82)
    if p_prog > 0:
        draw_particles(img, CENTER_PX[0], CENTER_PX[1], p_prog,
                       color=(255, 152, 0))

    draw_icon(img, "Craftnote", cx, cy, opacity=icon_op)

    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Ein System, das bestehende Tools integriert — oder sogar ersetzt.",
                     H - 55, opacity=lerp_ease(f, 50, 68), size=13)

def scene06(f, img):
    """OneDrive → Warenwirtschaft"""
    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1], scale=0.7, opacity=0.6)

    od_pos = icon_px("OneDrive")
    mod_pos = (int(W * 0.72), H // 2)

    # Stream
    stream_p = lerp_ease(f, 5, 48)
    draw_line(img, od_pos[0], od_pos[1], mod_pos[0], mod_pos[1],
              progress=stream_p, color=CYAN, width=2, opacity=0.9)
    draw_line(img, od_pos[0], od_pos[1], CENTER_PX[0], CENTER_PX[1],
              progress=1.0, color=BLUE, width=1, opacity=0.35)

    draw_icon(img, "OneDrive", od_pos[0], od_pos[1], glowing=True)

    mod_op = lerp_ease(f, 44, 64)
    draw_module_card(img, mod_pos[0], mod_pos[1],
                     "Warenwirtschaft",
                     ["Artikel & Material", "Lagerbestände", "Bestellungen", "Lieferanten"],
                     opacity=mod_op, color=CYAN, w=210)

    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Material wird automatisch organisiert.",
                     H - 55, opacity=lerp_ease(f, 52, 70), size=14)

def scene07(f, img):
    """Projektverwaltung"""
    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1], scale=0.55, opacity=0.45)

    ware_pos = (int(W * 0.30), int(H * 0.40))
    proj_pos = (int(W * 0.66), int(H * 0.40))
    time_pos = (int(W * 0.66), int(H * 0.72))

    # Warenwirtschaft → Projektverwaltung stream
    conn_p = lerp_ease(f, 18, 55)
    draw_line(img, ware_pos[0]+105, ware_pos[1],
              proj_pos[0]-105, proj_pos[1],
              progress=conn_p, color=CYAN, width=2)

    # Projektverwaltung → Zeiterfassung
    t2_p = lerp_ease(f, 50, 75)
    draw_line(img, proj_pos[0], proj_pos[1]+60,
              time_pos[0], time_pos[1]-55,
              progress=t2_p, color=PURPLE, width=1)

    draw_module_card(img, ware_pos[0], ware_pos[1], "Warenwirtschaft",
                     ["Artikel & Material", "Lagerbestände"],
                     opacity=lerp_ease(f, 0, 18), color=CYAN, w=200)

    draw_module_card(img, proj_pos[0], proj_pos[1], "Projektverwaltung",
                     ["Projekte & Aufgaben", "Fortschritt", "Ressourcen", "Meilensteine"],
                     opacity=lerp_ease(f, 48, 68), color=(0,220,200), w=220)

    draw_module_card(img, time_pos[0], time_pos[1], "Zeiterfassung",
                     ["Arbeitszeiten", "Auswertungen"],
                     opacity=lerp_ease(f, 58, 76), color=PURPLE, w=200)

    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Projekte werden strukturiert verwaltet.",
                     H - 55, opacity=lerp_ease(f, 56, 74), size=14)

def scene08(f, img):
    """Automatische Kommunikation"""
    draw_glow_node(img, CENTER_PX[0], CENTER_PX[1], scale=0.5, opacity=0.4)

    proj_pos = (CENTER_PX[0], int(H * 0.45))
    email_pos = icon_px("Email")
    od_pos   = icon_px("OneDrive")

    # Email streams
    for i, src in enumerate([(200, 160), (310, 290), (160, 420)]):
        p = lerp_ease(f, i*10, i*10+38)
        draw_line(img, src[0], src[1], proj_pos[0]-100, proj_pos[1],
                  progress=p, color=PURPLE, width=1, opacity=0.75)

    # OneDrive stream
    draw_line(img, od_pos[0], od_pos[1], proj_pos[0], proj_pos[1]+60,
              progress=lerp_ease(f, 18, 58), color=BLUE, width=1)

    draw_icon(img, "Email", email_pos[0], email_pos[1], glowing=True)
    draw_icon(img, "OneDrive", od_pos[0], od_pos[1], opacity=0.75)

    draw_module_card(img, proj_pos[0], proj_pos[1], "Projektverwaltung",
                     ["✉ E-Mail → Aufgabe", "📁 Datei angehängt",
                      "🔔 Update gesendet", "📋 Dok. verknüpft"],
                     opacity=lerp_ease(f, 0, 22), color=(0,220,200), w=255)

    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Dokumente und Kommunikation finden automatisch ihren Platz.",
                     H - 55, opacity=lerp_ease(f, 52, 70), size=13)

DASH_MODULES = [
    {"pos": (0.22, 0.30), "title": "Projekte",     "items": ["Aktive Projekte", "Aufgaben"],     "color": CYAN,         "w": 170},
    {"pos": (0.40, 0.30), "title": "Material",      "items": ["Bestände", "Bestellungen"],        "color": (0,220,200),  "w": 170},
    {"pos": (0.58, 0.30), "title": "Kommunikation", "items": ["E-Mails", "Benachrichtigung."],    "color": PURPLE,       "w": 170},
    {"pos": (0.76, 0.30), "title": "Dokumente",     "items": ["Dateien", "Verträge"],             "color": (255,152,0),  "w": 170},
    {"pos": (0.22, 0.68), "title": "Buchhaltung",   "items": ["Rechnungen", "BMD-Sync"],         "color": (229,57,53),  "w": 170},
    {"pos": (0.40, 0.68), "title": "Kalkulation",   "items": ["BLS-Import", "Positionen"],        "color": (255,107,53), "w": 170},
    {"pos": (0.58, 0.68), "title": "Zeiterfassung", "items": ["Arbeitszeiten", "Auswertung."],    "color": (76,175,80),  "w": 170},
    {"pos": (0.76, 0.68), "title": "Berichte",      "items": ["KPIs", "Auswertungen"],            "color": (0,188,212),  "w": 170},
]

def scene09(f, img):
    """Finale Übersicht: full dashboard"""
    # Scale from 1.15 → 1 (camera pulls back)
    scale = lerp_ease(f, 0, 55, 1.12, 1.0)
    sub = Image.fromarray(make_background())

    draw_glow_node(sub, CENTER_PX[0], CENTER_PX[1], scale=0.45, opacity=0.35)

    for i, m in enumerate(DASH_MODULES):
        mx = int(m["pos"][0] * W)
        my = int(m["pos"][1] * H)
        mo = lerp_ease(f, i*4, i*4+20)
        draw_line(sub, CENTER_PX[0], CENTER_PX[1], mx, my,
                  progress=1.0, color=m["color"], width=1,
                  opacity=lerp_ease(f, i*4, i*4+20) * 0.25)
        draw_module_card(sub, mx, my, m["title"], m["items"],
                         opacity=mo, color=m["color"], w=m["w"])

    # Scale
    new_w = int(W * scale)
    new_h = int(H * scale)
    sub_s = sub.resize((new_w, new_h), Image.LANCZOS)
    ox = (W - new_w) // 2
    oy = (H - new_h) // 2
    img.paste(sub_s, (ox, oy))

    draw = ImageDraw.Draw(img)
    draw_text_center(draw, "Aus vielen Programmen wird eine Plattform.",
                     H - 55, opacity=lerp_ease(f, 60, 78), size=14)

def scene10(f, img):
    """Finale Botschaft: tagline + fade to black"""
    # Ambient glow
    glow_alpha = int((0.25 + math.sin(f * 0.1) * 0.08) * 200)
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    r = 320
    for i in range(6, 0, -1):
        ri = r * i // 5
        ai = int(glow_alpha * i / 6)
        d.ellipse([CENTER_PX[0]-ri, CENTER_PX[1]-ri,
                   CENTER_PX[0]+ri, CENTER_PX[1]+ri],
                  fill=(*BLUE, ai))
    img_a = img.convert("RGBA")
    img.paste(Image.alpha_composite(img_a, layer).convert("RGB"))

    # Horizontal line
    line_w = int(lerp_ease(f, 5, 22) * 320)
    if line_w > 0:
        draw = ImageDraw.Draw(img)
        lx0 = CENTER_PX[0] - line_w//2
        lx1 = CENTER_PX[0] + line_w//2
        draw.line([(lx0, CENTER_PX[1]-52), (lx1, CENTER_PX[1]-52)],
                  fill=(*CYAN, int(lerp_ease(f, 5, 20) * 120)), width=1)

    draw = ImageDraw.Draw(img)
    # Line 1
    op1 = lerp_ease(f, 10, 30)
    try:
        font_big = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 52)
        font_big_bold = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    except:
        font_big = font_big_bold = ImageFont.load_default()

    draw.text((CENTER_PX[0], CENTER_PX[1] - 20), "Ein Betriebssystem",
              font=font_big, anchor="mm",
              fill=(*WHITE, int(op1 * 245)))

    # Line 2 (gradient-ish: cyan color)
    op2 = lerp_ease(f, 30, 52)
    draw.text((CENTER_PX[0], CENTER_PX[1] + 48), "für deinen Betrieb.",
              font=font_big_bold, anchor="mm",
              fill=(*CYAN, int(op2 * 245)))

    # Subtitle
    op3 = lerp_ease(f, 52, 68)
    draw_text_center(draw, "Übersichtlich · Strukturiert · Für deinen Betrieb gebaut",
                     CENTER_PX[1] + 100, opacity=op3, size=14)

    # Fade to black
    fade = lerp_ease(f, 74, 89)
    if fade > 0:
        overlay = Image.new("RGB", (W, H), (0,0,0))
        img.paste(overlay, mask=Image.fromarray(
            np.full((H, W), int(fade * 255), dtype=np.uint8)))

# ─── Scene dispatch ───────────────────────────────────────────────────────────
SCENES = [scene01, scene02, scene03, scene04, scene05,
          scene06, scene07, scene08, scene09, scene10]
SCENE_LEN = 90  # frames per scene

def render_frame(global_frame: int) -> np.ndarray:
    scene_idx = global_frame // SCENE_LEN
    local_frame = global_frame % SCENE_LEN
    if scene_idx >= len(SCENES):
        scene_idx = len(SCENES) - 1

    bg = make_background(global_frame)
    img = Image.fromarray(bg)
    SCENES[scene_idx](local_frame, img)
    return np.array(img)

# ─── Main render loop ─────────────────────────────────────────────────────────
def main():
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using ffmpeg: {ffmpeg_path}")
    print(f"Rendering {TOTAL_FRAMES} frames @ {W}x{H} {FPS}fps → {OUT_PATH}")

    writer = imageio.get_writer(
        OUT_PATH,
        fps=FPS,
        codec="libx264",
        quality=None,
        ffmpeg_params=["-crf", "20", "-preset", "fast",
                       "-pix_fmt", "yuv420p"],
        ffmpeg_log_level="warning",
    )

    for f in range(TOTAL_FRAMES):
        frame = render_frame(f)
        writer.append_data(frame)
        if f % 30 == 0:
            pct = f / TOTAL_FRAMES * 100
            scene = f // SCENE_LEN + 1
            print(f"  {pct:5.1f}% — frame {f:4d}/{TOTAL_FRAMES} (Szene {scene}/10)", flush=True)

    writer.close()
    size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"\nFertig! → {OUT_PATH}  ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()
