import json, os, zipfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "pack")
ITEM = os.path.join(PACK, "assets/minecraft/textures/item")
os.makedirs(ITEM, exist_ok=True)

BLACK = (14, 10, 20, 255)
DARK = (34, 16, 48, 255)
RED = (220, 20, 40, 255)
DRED = (140, 8, 24, 255)
PURPLE = (150, 60, 230, 255)
DPURP = (88, 28, 140, 255)
GLOW = (255, 90, 120, 255)
T = (0, 0, 0, 0)


def canvas():
    return Image.new("RGBA", (16, 16), T)


def save_strip(frames, name, frametime=None, frame_order=None):
    strip = Image.new("RGBA", (16, 16 * len(frames)), T)
    for i, f in enumerate(frames):
        strip.paste(f, (0, 16 * i))
    strip.save(os.path.join(ITEM, name + ".png"))
    if len(frames) > 1:
        anim = {"interpolate": False, "frametime": frametime or 4}
        if frame_order:
            anim["frames"] = frame_order
        with open(os.path.join(ITEM, name + ".png.mcmeta"), "w") as fh:
            json.dump({"animation": anim}, fh, indent=2)


def tint_pulse(base, color, amt):
    im = base.copy()
    p = im.load()
    for x in range(16):
        for y in range(16):
            r, g, b, a = p[x, y]
            if a:
                p[x, y] = (int(r + (color[0] - r) * amt),
                           int(g + (color[1] - g) * amt),
                           int(b + (color[2] - b) * amt), a)
    return im


def sword(blade, edge, guard, grip, pommel):
    im = canvas()
    p = im.load()
    for i in range(2, 13):
        x, y = i + 1, 14 - i - 1
        p[x, y] = blade
        p[x - 1, y] = edge
    p[14, 1] = edge
    p[13, 1] = edge
    p[14, 2] = blade
    for d in range(-2, 3):
        p[3 + d, 11 - d] = guard
    p[2, 12] = grip
    p[1, 13] = grip
    p[0, 14] = pommel
    p[1, 14] = grip
    return im


SWORDS = {
    "wooden_sword": ((70, 40, 90, 255), DPURP, PURPLE, DARK, BLACK),
    "stone_sword": ((60, 55, 70, 255), BLACK, DPURP, DARK, BLACK),
    "iron_sword": ((120, 110, 140, 255), DPURP, RED, DARK, BLACK),
    "golden_sword": ((200, 40, 90, 255), DRED, PURPLE, DARK, BLACK),
    "diamond_sword": (PURPLE, DPURP, RED, DARK, BLACK),
    "netherite_sword": (BLACK, RED, PURPLE, DARK, DRED),
}
for name, cols in SWORDS.items():
    base = sword(*cols)
    if name in ("diamond_sword", "netherite_sword"):
        pulse = RED if name == "netherite_sword" else GLOW
        save_strip([base] + [tint_pulse(base, pulse, a) for a in (0.25, 0.5, 0.25)], name, 5)
    else:
        save_strip([base], name)


def tool(kind, head, edge, stick):
    im = canvas()
    p = im.load()
    for i in range(9):
        p[2 + i, 13 - i] = stick
    if kind == "pickaxe":
        for x in range(4, 14):
            p[x, 3 + (0 if 6 < x < 11 else (1 if x in (5, 11) else 2))] = head
        p[3, 5] = edge
        p[14, 5] = edge
    elif kind == "axe":
        for xy in [(8,3),(9,3),(10,3),(8,4),(9,4),(10,4),(11,4),(9,5),(10,5),(11,5),(10,6)]:
            p[xy] = head
        p[11, 6] = edge
    elif kind == "shovel":
        for xy in [(11,2),(12,2),(10,3),(11,3),(12,3),(13,3),(11,4),(12,4)]:
            p[xy] = head
    else:
        for xy in [(7,3),(8,3),(9,3),(10,3),(11,3),(7,4),(11,4)]:
            p[xy] = head
    return im


TIERS = {"wooden": (DPURP, BLACK), "stone": (DARK, DPURP), "iron": ((120,110,140,255), DPURP),
         "golden": ((200,40,90,255), DRED), "diamond": (PURPLE, RED), "netherite": (BLACK, RED)}
for tier, (h, e) in TIERS.items():
    for kind in ("pickaxe", "axe", "shovel", "hoe"):
        base = tool(kind, h, e, DARK)
        if tier == "netherite":
            save_strip([base] + [tint_pulse(base, RED, a) for a in (0.3, 0.6, 0.3)], tier + "_" + kind, 6)
        else:
            save_strip([base], tier + "_" + kind)


def totem(body, trim, face, eye):
    im = canvas()
    p = im.load()
    for y in range(2, 14):
        w = 5 if y < 7 else (7 if y < 10 else 5)
        for x in range(8 - w // 2, 8 + w // 2 + 1):
            p[x, y] = body
    for x in range(4, 12):
        p[x, 2] = trim
    for x in range(3, 13):
        p[x, 7] = trim
    for y in range(2, 14):
        p[5, y] = trim if y % 2 else body
    for x in (6, 9):
        p[x, 5] = eye
    p[7, 6] = face
    p[8, 6] = face
    for x in (6, 7, 8, 9):
        p[x, 8] = eye
    return im


default = totem((235, 190, 50, 255), (60, 140, 60, 255), (200, 150, 40, 255), (30, 30, 30, 255))
themed = totem(PURPLE, RED, DPURP, BLACK)

skin = Image.open(os.path.join(ROOT, "skin.jpg")).convert("RGBA")
face = skin.crop((8, 8, 16, 16)).resize((12, 12), Image.NEAREST)
framed = canvas()
fp = framed.load()
for x in range(16):
    for y in range(16):
        if x in (0, 15) or y in (0, 15):
            fp[x, y] = RED
        elif x in (1, 14) or y in (1, 14):
            fp[x, y] = PURPLE
framed.alpha_composite(face, (2, 2))

glow = [tint_pulse(themed, GLOW, a) for a in (0.0, 0.35, 0.7, 0.35)]
frames = [default] + glow + [framed, themed]
order = [{"index": 0, "time": 40}]
order += [{"index": i, "time": 4} for i in (1, 2, 3, 4, 1, 2, 3, 4)]
order += [{"index": 5, "time": 60}, {"index": 6, "time": 40}]
save_strip(frames, "totem_of_undying", frame_order=order)

with open(os.path.join(PACK, "pack.mcmeta"), "w") as f:
    json.dump({"pack": {"pack_format": 46, "supported_formats": [34, 99],
                        "description": "Red Black Purple YT Pack"}}, f, indent=2)
framed.resize((64, 64), Image.NEAREST).save(os.path.join(PACK, "pack.png"))

os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
zp = os.path.join(ROOT, "dist/TexturePack.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d, _, files in os.walk(PACK):
        for fn in files:
            full = os.path.join(d, fn)
            z.write(full, os.path.relpath(full, PACK))
print("OK", zp)
