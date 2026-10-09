import base64
import io
import json
import math
import random
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIZE = (1200, 340)
PHOTO_SIZE = (700, 458)
SEED = 7
BREATH_LAYERS = 6
BREATH_SHIFT = 6
BREATH_DUR = "5.2s"
FACE = dict(cx=378, cy=135, rx=120, ry=125)
FACE_W = 1.0
HAND = dict(cx=320, cy=275, rx=165, ry=105)
HAND_W = 0.75
LID_BOX = (300, 98, 460, 142)
EYES = [dict(x0=308, x1=344, y0=100, y1=126),
        dict(x0=416, x1=451, y0=108, y1=138)]
LID_SS = 4
LID_REDNESS = 14
LID_KEEP_LUM = 62
LID_TOP_PAD = 0.5
LASH = (22, 20, 23)
BLINK_CYCLE = "9s"
BLINK_STARTS = [30, 82, 85.4]
STATIC_DROPS = 60
RUN_DROPS = 16
TEAR_BANDS = 8
NOISE_BLOCKS = 16
GLITCH_CYCLE = "6.4s"
A_SLOTS = [(38, 38.8), (38.8, 39.6), (39.6, 40.5)]
B_EDGES = [86, 87.2, 88.3, 89.4, 90, 91.2, 92.4, 93.5, 94.7, 96]
B_SLOTS = list(zip(B_EDGES, B_EDGES[1:]))
SLICES = [(40, 58, 566, 58, 566, 94, 40, 110),
          (40, 110, 566, 94, 566, 122, 40, 134),
          (40, 134, 566, 122, 566, 148, 40, 158),
          (40, 158, 566, 148, 566, 174, 40, 184),
          (40, 184, 566, 174, 566, 214, 40, 214)]
SHARDS = [
    ("polygon", "604,26 668,8 646,62 598,58", "glass", "large"),
    ("polygon", "700,286 762,300 716,326 692,312", "glass2", "large"),
    ("polygon", "1044,44 1102,30 1086,80 1038,74", "glass", "large"),
    ("polygon", "1128,196 1172,186 1166,232 1124,224", "glass2", "large"),
    ("polygon", "866,14 906,4 892,40", "glass", "large"),
    ("polygon", "952,314 998,326 956,336", "glass2", "large"),
    ("polygon", "556,196 590,186 582,220 552,216", "glass2", "large"),
    ("polyline", "640,96 672,88 690,104", "", "line"),
    ("polyline", "1096,132 1134,124 1150,138", "", "line"),
    ("polyline", "820,268 848,258 870,272", "", "line"),
    ("polygon", "748,120 760,116 754,134", "", "tiny"),
    ("polygon", "1010,236 1024,232 1014,252", "", "tiny"),
    ("polygon", "676,214 686,210 680,226", "", "tiny"),
]
CRACKS = [(58, 109, 286, 102, 0.16), (310, 101, 512, 95, 0.10),
          (72, 133, 248, 129, 0.30), (336, 126, 498, 122, 0.09),
          (90, 158, 330, 153, 0.11)]
THEMES = {
    "dark": dict(bg="#000000", fade="#000000", fade_mid="0.88", vign_top="0.5",
                 vign_bottom="0.55", glass_a="#e8f0f6", glass_b="#9fb6c6",
                 glass_op=("0.12", "0.05", "0.10"), glass2="#cfe0ec",
                 glass2_op=("0.14", "0.02"), overlay="#05070a", overlay_op="0.50",
                 scan="#ffffff", scan_op="0.02", shard="#dfe6ec",
                 shard_op=("0.18", "0.10", "0.2"), name="#aab3bd",
                 crack="#dfe6ec", crack_accent="#7f9bb0", crack_op=None,
                 accent="#7f9bb0", accent2="#3b444d", tagline="#9aa5b0",
                 stack="#616973", tag_bg="#0b0e12", tag_stroke="#2b333b",
                 tag_fill=("#aab3bd", "#aab3bd", "#aab3bd"), frame="#1e242a",
                 drop_core="#cfe0ec", drop_rim="#000000", drop_rim_op="0.55",
                 drop_hi="#f2f6fa", trail_op="0.28", cp_red="#ff2a55",
                 cp_cyan="#00e5ff", cp_blend="screen", cp_hi="#f2f6fa",
                 flash_op="0.07"),
    "light": dict(bg="#f6f8fa", fade="#f6f8fa", fade_mid="0.9", vign_top="0.35",
                  vign_bottom="0.4", glass_a="#57606a", glass_b="#8c959f",
                  glass_op=("0.10", "0.04", "0.08"), glass2="#57606a",
                  glass2_op=("0.12", "0.02"), overlay="#f6f8fa", overlay_op="0.12",
                  scan="#1f2328", scan_op="0.018", shard="#57606a",
                  shard_op=("0.22", "0.14", "0.25"), name="#424a53",
                  crack="#57606a", crack_accent="#4b6a82",
                  crack_op=(0.22, 0.14, 0.35, 0.12, 0.15),
                  accent="#4b6a82", accent2="#d0d7de", tagline="#424a53",
                  stack="#6e7781", tag_bg="#ffffff", tag_stroke="#d0d7de",
                  tag_fill=("#57606a", "#57606a", "#424a53"), frame="#d0d7de",
                  drop_core="#57606a", drop_rim="#24292f", drop_rim_op="0.42",
                  drop_hi="#ffffff", trail_op="0.30", cp_red="#e0003c",
                  cp_cyan="#0093b0", cp_blend="multiply", cp_hi="#1f2328",
                  flash_op="0.05"),
}


def number(value):
    return f"{value:.3f}".rstrip("0").rstrip(".")


def frames(name, base, events):
    points = {0: base, 100: base}
    for start, end, decl in sorted(events):
        points[end] = base
        points[start] = decl
    body = " ".join(f"{number(p)}% {{{points[p]}}}" for p in sorted(points))
    return f"@keyframes {name} {{{body}}}"


def ramp(name, points):
    body = " ".join(f"{number(pct)}% {{opacity:{opacity}}}"
                    for pct, opacity in sorted([(0, 0), *points, (100, 0)]))
    return f"@keyframes {name} {{{body}}}"


def png_uri(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")


def make_breath_masks():
    masks = [Image.new("L", (175, 115)) for _ in range(BREATH_LAYERS)]
    layers = [mask.load() for mask in masks]
    for py in range(115):
        for px in range(175):
            def bump(eye):
                radius = math.hypot((px * 4 - eye["cx"]) / eye["rx"],
                                    (py * 4 - eye["cy"]) / eye["ry"])
                t = max(0.0, min(1.0, (1 - radius) / 0.7))
                return t * t * (3 - 2 * t)
            amount = 1 - (1 - FACE_W * bump(FACE)) * (1 - HAND_W * bump(HAND))
            for k, pixels in enumerate(layers, 1):
                v = max(0.0, min(1.0, amount * BREATH_LAYERS - (k - 1)))
                pixels[px, py] = round(255 * v * v * (3 - 2 * v))
    return [png_uri(mask) for mask in masks]


def polyfit2(xs, ys):
    if len(xs) < 3:
        raise ValueError(f"found only {len(xs)} matching columns (need at least 3)")
    center = sum(xs) / len(xs)
    offsets = [x - center for x in xs]
    moments = [sum(z ** degree for z in offsets) for degree in range(5)]
    rhs = [sum(y * z ** degree for z, y in zip(offsets, ys))
           for degree in (2, 1, 0)]
    matrix = [[moments[4], moments[3], moments[2], rhs[0]],
              [moments[3], moments[2], moments[1], rhs[1]],
              [moments[2], moments[1], moments[0], rhs[2]]]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda row: abs(matrix[row][col]))
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        if math.isclose(matrix[col][col], 0.0, abs_tol=1e-9):
            raise ValueError("quadratic fit is degenerate")
        for row in range(col + 1, 3):
            factor = matrix[row][col] / matrix[col][col]
            for index in range(col, 4):
                matrix[row][index] -= factor * matrix[col][index]
    coefficients = [0.0] * 3
    for row in range(2, -1, -1):
        coefficients[row] = (
            matrix[row][3] -
            sum(matrix[row][col] * coefficients[col] for col in range(row + 1, 3))
        ) / matrix[row][row]

    def evaluate(x):
        z = x - center
        return (coefficients[0] * z + coefficients[1]) * z + coefficients[2]

    return evaluate


def make_lids(photo):
    x0, y0, x1, y1 = LID_BOX
    width, height = x1 - x0, y1 - y0
    source = photo.crop(LID_BOX)
    source_pixels = source.load()
    photo_pixels = photo.load()
    eye_spans = []
    for index, eye in enumerate(EYES, 1):
        spans = {}
        for x in range(eye["x0"], eye["x1"]):
            ys = [y for y in range(eye["y0"], eye["y1"])
                  if photo_pixels[x, y][0] -
                  (photo_pixels[x, y][1] + photo_pixels[x, y][2]) / 2 >
                  LID_REDNESS]
            if len(ys) >= 2:
                spans[x] = (min(ys), max(ys))
        xs = sorted(spans)
        try:
            top_fit = polyfit2(xs, [spans[x][0] for x in xs])
            bottom_fit = polyfit2(xs, [spans[x][1] for x in xs])
        except ValueError as exc:
            area = (eye["x0"], eye["y0"], eye["x1"], eye["y1"])
            raise SystemExit(f"Eye {index} in search area {area}: {exc}") from exc
        eye_spans.append((eye, {x: (top_fit(x), bottom_fit(x)) for x in xs}))

    result = {}
    for kind in ("half", "closed"):
        patch = Image.new("RGBA", (width, height))
        patch_pixels = patch.load()
        lash_points = []
        for eye, spans in eye_spans:
            for x, (top, bottom) in spans.items():
                top -= LID_TOP_PAD
                bottom += 0.8
                cover_to = bottom if kind == "closed" else top + 0.55 * (bottom - top)
                lx = x - x0
                for y in range(int(top) - 1, int(bottom) + 2):
                    ly = y - y0
                    if not (0 <= ly < height):
                        continue
                    alpha = max(0.0, min(1.0, y + 1 - top)) * max(
                        0.0, min(1.0, cover_to - y + 0.5))
                    if alpha <= 0:
                        continue
                    mirror_y = int(round(bottom + (bottom - y) * 0.6 + 2)) - y0
                    mirror_y = max(0, min(height - 1, mirror_y))
                    r, g, b = source_pixels[lx, mirror_y]
                    original_r, original_g, original_b = source_pixels[lx, ly]
                    lum = (original_r + original_g + original_b) / 3
                    red = original_r - (original_g + original_b) / 2
                    keep = max(0.0, min(1.0, (LID_KEEP_LUM - lum) / 20)) * max(
                        0.0, min(1.0, (12 - red) / 8))
                    alpha *= 1 - keep
                    t = (y - top) / max(1.0, bottom - top)
                    shade = 0.38 + 0.54 * (t * t * (3 - 2 * t))
                    patch_pixels[lx, ly] = (
                        int(r * shade), int(g * shade), int(b * shade),
                        int(255 * alpha))
                lash_points.append((x, cover_to - 0.6))
        alpha = patch.getchannel("A").filter(ImageFilter.GaussianBlur(0.6))
        patch.putalpha(alpha)
        big = patch.resize((width * LID_SS, height * LID_SS),
                           Image.Resampling.BICUBIC)
        draw = ImageDraw.Draw(big)
        for eye in EYES:
            points = [(x, y) for x, y in lash_points
                      if eye["x0"] <= x < eye["x1"]]
            count = len(points)
            for index, (x, y) in enumerate(points):
                t = index / max(1, count - 1)
                thick = (1.3 + 1.6 * (1 - abs(2 * t - 1) ** 2)
                         if kind == "closed" else
                         1.6 + 1.8 * (1 - abs(2 * t - 1) ** 2))
                radius = thick * LID_SS / 2
                cx, cy = (x - x0 + 0.5) * LID_SS, (y - y0) * LID_SS
                draw.ellipse((cx - radius, cy - radius,
                              cx + radius, cy + radius), fill=(*LASH, 255))
        result[kind] = big.resize((width, height), Image.Resampling.LANCZOS)
    preview_dir = HERE / ".preview"
    preview_dir.mkdir(exist_ok=True)
    for kind, patch in result.items():
        patch.save(preview_dir / f"lid-{kind}.png", optimize=True)
    preview = Image.new("RGB", (width * 6 * 3, height * 6))
    source = photo.crop(LID_BOX).convert("RGBA")
    for index, kind in enumerate((None, "half", "closed")):
        frame = source.copy()
        if kind:
            frame.alpha_composite(result[kind])
        preview.paste(frame.convert("RGB").resize((width * 6, height * 6),
                      Image.Resampling.LANCZOS), (index * width * 6, 0))
    preview.save(preview_dir / "lid-preview.png", optimize=True)
    return {kind: png_uri(patch) for kind, patch in result.items()}


def drops_svg(colors, rnd):
    body, css = [], []
    flickering = set(rnd.sample(range(STATIC_DROPS), STATIC_DROPS // 4))

    def shape(radius, trail=0):
        r = number(radius)
        parts = []
        if trail:
            parts.append(f'<rect x="{number(-0.45 * radius)}" y="-{number(trail)}" '
                         f'width="{number(0.9 * radius)}" height="{number(trail - radius)}" '
                         f'rx="{number(0.45 * radius)}" fill="url(#dropTrail)"/>')
        parts.extend((
            f'<ellipse rx="{r}" ry="{number(1.15 * radius)}" fill="url(#dropBody)"/>',
            f'<ellipse cx="{number(-0.35 * radius)}" cy="{number(-0.42 * radius)}" '
            f'rx="{number(0.36 * radius)}" ry="{number(0.28 * radius)}" '
            f'fill="{colors["drop_hi"]}" opacity="0.8"/>',
            f'<circle cx="{number(0.3 * radius)}" cy="{number(0.55 * radius)}" '
            f'r="{number(0.22 * radius)}" fill="{colors["drop_hi"]}" opacity="0.35"/>'))
        return "".join(parts)

    for i in range(STATIC_DROPS):
        x, y = rnd.uniform(610, 1192), rnd.uniform(6, 334)
        radius = 0.6 + 1.2 * rnd.random() ** 2
        style = ""
        if i in flickering:
            duration = rnd.uniform(4, 9)
            delay = -rnd.uniform(0, duration)
            style = (f' style="animation: flicker {number(duration)}s ease-in-out '
                     f'{number(delay)}s infinite"')
        body.append(f'<g transform="translate({number(x)} {number(y)})"{style}>'
                    f'{shape(radius)}</g>')
    css.append("@keyframes flicker {0%,100% {opacity:1} 50% {opacity:.55}}")
    css.append("@keyframes dropfade {0% {opacity:0} 3%,96% {opacity:1} 100% {opacity:0}}")
    for i in range(RUN_DROPS):
        x = rnd.uniform(620, 1190)
        radius, trail = rnd.uniform(1.8, 3), rnd.uniform(16, 60)
        duration = rnd.uniform(7, 16)
        delay = -rnd.uniform(0, duration)
        segments = rnd.randint(5, 8)
        slow = [rnd.uniform(2, 8) if j % 2 == 0 else 0 for j in range(segments)]
        fast = [rnd.uniform(0.8, 1.2) if j % 2 else 0 for j in range(segments)]
        fast_total = sum(fast)
        dy = [step if j % 2 == 0 else
              (402 - sum(slow)) * fast[j] / fast_total for j, step in enumerate(slow)]
        weights = [rnd.uniform(2.2, 3.2) if j % 2 == 0 else
                   rnd.uniform(0.25, 0.5) for j in range(segments)]
        points = [(0, 0, -30)]
        pct, y = 0, -30
        for j in range(segments):
            pct += 100 * weights[j] / sum(weights)
            y += dy[j]
            points.append((100 if j == segments - 1 else pct,
                           rnd.uniform(-4, 4), 372 if j == segments - 1 else y))
        keyframes = " ".join(f'{number(p)}% {{transform:translate({number(dx)}px,'
                             f'{number(py)}px)}}' for p, dx, py in points)
        css.append(f"@keyframes run{i} {{{keyframes}}}")
        body.append(f'<g class="rd" style="animation:run{i} {number(duration)}s '
                    f'cubic-bezier(.5,0,.8,1) {number(delay)}s infinite,'
                    f'dropfade {number(duration)}s linear {number(delay)}s infinite">'
                    f'<g transform="translate({number(x)} 0)">{shape(radius, trail)}</g></g>')
    return "\n".join(body), css


def shards_svg(colors, rnd):
    groups = [[], [], []]
    css = []
    for i, (tag, points, fill, kind) in enumerate(SHARDS):
        coords = [tuple(map(float, pair.split(","))) for pair in points.split()]
        ys = [point[1] for point in coords]
        start, end = -(max(ys) + 12), 352 - min(ys)
        speed = rnd.uniform(*( (9, 13) if kind == "large" else
                               (8, 11) if kind == "line" else (16, 24)))
        duration = (end - start) / speed
        delay = -rnd.uniform(0, duration)
        dx = rnd.choice((-1, 1)) * rnd.uniform(6, 22)
        rotation = rnd.choice((-1, 1)) * rnd.uniform(
            *( (8, 28) if kind == "large" else (60, 160) if kind == "tiny" else (8, 28)))
        css.append(f'@keyframes fall{i} {{0% {{transform:translate(0px,'
                   f'{number(start)}px) rotate(0deg);opacity:0}} '
                   f'6%,94% {{opacity:1}} 100% {{transform:translate('
                   f'{number(dx)}px,{number(end)}px) rotate({number(rotation)}deg);'
                   f'opacity:0}}}}')
        attr = f' fill="url(#{fill})"' if fill else ""
        groups[0 if kind == "large" else 1 if kind == "line" else 2].append(
            f'<{tag} points="{points}"{attr} style="transform-box:fill-box;'
            f'transform-origin:center;animation:fall{i} {number(duration)}s linear '
            f'{number(delay)}s infinite"/>')
    a, b, c = ("\n".join(group) for group in groups)
    svg = (f'<g stroke="{colors["shard"]}" stroke-opacity="{colors["shard_op"][0]}" '
           f'stroke-width="1">{a}</g>\n'
           f'<g stroke="{colors["shard"]}" stroke-opacity="{colors["shard_op"][1]}" '
           f'stroke-width="1" fill="none">{b}</g>\n'
           f'<g fill="{colors["shard"]}" opacity="{colors["shard_op"][2]}">{c}</g>')
    return svg, css


def name_svg(colors, rnd):
    body, css, defs = [], [], []
    base = "transform:translate(0px,0px);opacity:0"
    rgb_offsets = []
    for start, end in B_SLOTS:
        red_dx, red_dy = rnd.uniform(-14, -3), rnd.uniform(-2, 2)
        cyan_dx = -red_dx + rnd.uniform(-1, 1)
        cyan_dy = -red_dy + rnd.uniform(-1, 1)
        rgb_offsets.append((start, end, (red_dx, red_dy), (cyan_dx, cyan_dy)))
    for channel, sign in (("red", -1), ("cyan", 1)):
        events = [(38, 40.5, f"transform:translate({3 * sign}px,0px);opacity:.8")]
        for start, end, red, cyan in rgb_offsets:
            dx, dy = red if channel == "red" else cyan
            events.append((start, end, f"transform:translate({number(dx)}px,"
                           f"{number(dy)}px);opacity:.85"))
        css.append(frames(f"rgb-{channel}", base, events))
        body.append(f'<use href="#nm" xlink:href="#nm" fill="{colors["cp_" + channel]}" '
                    f'opacity="0" style="mix-blend-mode:{colors["cp_blend"]};'
                    f'animation:rgb-{channel} {GLITCH_CYCLE} step-end infinite"/>')
    offsets = [(0, 0, "1.0"), (4, -2, "0.82"), (-5, 1, "0.7"),
               (6, 2, "0.88"), (-3, -3, "0.66")]
    for i, (x, y, opacity) in enumerate(offsets, 1):
        events = []
        for start, end in rnd.sample(A_SLOTS, rnd.randint(2, 3)):
            events.append((start, end, f"transform:translate({rnd.choice((-1, 1)) * rnd.randint(2, 7)}px,0px)"))
        for start, end in rnd.sample(B_SLOTS, rnd.randint(6, 8)):
            dx = rnd.choice((-1, 1)) * rnd.randint(6, 20)
            skew = " skewX(-12deg)" if start == 90 else ""
            events.append((start, end, f"transform:translate({dx}px,0px){skew}"))
        css.append(frames(f"gl{i}", "transform:translate(0px,0px)", events))
        body.append(f'<g clip-path="url(#s{i})"><g class="gl gl{i}" '
                    f'style="animation:gl{i} {GLITCH_CYCLE} step-end infinite">'
                    f'<g transform="translate({x},{y})" opacity="{opacity}">'
                    f'<use href="#nm" xlink:href="#nm" fill="{colors["name"]}"/>'
                    f'</g></g></g>')
    for i in range(TEAR_BANDS):
        y, height = rnd.uniform(98, 154), rnd.uniform(2, 9)
        defs.append(f'<clipPath id="tb{i}"><rect x="40" y="{number(y)}" '
                    f'width="530" height="{number(height)}"/></clipPath>')
        fill = (colors["name"], colors["cp_red"], colors["cp_cyan"])[i % 3]
        slots = rnd.sample(B_SLOTS, rnd.randint(2, 4))
        if i < 2:
            slots.append(rnd.choice(A_SLOTS))
        events = []
        for start, end in slots:
            distance = rnd.randint(6, 14) if start < 50 else rnd.randint(12, 48)
            dx = rnd.choice((-1, 1)) * distance
            events.append((start, end, f"transform:translate({dx}px,0px);opacity:1"))
        css.append(frames(f"tear{i}", base, events))
        body.append(f'<g clip-path="url(#tb{i})"><use href="#nm" xlink:href="#nm" '
                    f'fill="{fill}" opacity="0" style="animation:tear{i} {GLITCH_CYCLE} '
                    f'step-end infinite"/></g>')
    for i in range(NOISE_BLOCKS):
        x, y = rnd.uniform(60, 540), rnd.uniform(92, 162)
        width, height = rnd.uniform(6, 70), rnd.uniform(1.5, 7)
        fill = rnd.choice((colors["cp_red"], colors["cp_cyan"],
                           colors["name"], colors["cp_hi"]))
        slots = rnd.sample(B_SLOTS, rnd.randint(1, 3))
        if i < 3:
            slots.append(rnd.choice(A_SLOTS))
        css.append(frames(f"noise{i}", "opacity:0",
                          [(start, end, "opacity:.9") for start, end in slots]))
        body.append(f'<rect x="{number(x)}" y="{number(y)}" '
                    f'width="{number(width)}" height="{number(height)}" '
                    f'fill="{fill}" opacity="0" style="animation:noise{i} {GLITCH_CYCLE} '
                    f'step-end infinite"/>')
    css.append(frames("tearline", "opacity:0;transform:translateY(0px)",
                      [(87, 87.8, "opacity:.7;transform:translateY(150px)"),
                       (87.8, 88.6, "opacity:.7;transform:translateY(126px)"),
                       (88.6, 89.4, "opacity:.7;transform:translateY(104px)")]))
    body.append(f'<rect x="40" y="0" width="526" height="1.5" '
                f'fill="{colors["cp_hi"]}" opacity="0" style="animation:tearline '
                f'{GLITCH_CYCLE} step-end infinite"/>')
    css.append(frames("silhouette", base,
                      [(90, 91.2, "transform:translate(8px,0px) skewX(-12deg);opacity:.9")]))
    body.append(f'<use href="#nm" xlink:href="#nm" fill="{colors["cp_red"]}" '
                f'opacity="0" style="animation:silhouette {GLITCH_CYCLE} step-end infinite"/>')
    for i, (x1, y1, x2, y2, dark_op) in enumerate(CRACKS):
        opacity = colors["crack_op"][i] if colors["crack_op"] else dark_op
        color = colors["crack_accent"] if i == 2 else colors["crack"]
        events = [(39.6, 40.5, "opacity:.4"), (87.2, 88.3, "opacity:.35"),
                  (89.4, 90, "opacity:.1"), (91.2, 92.4, "opacity:.4")]
        css.append(frames(f"crack{i}", "opacity:1", events))
        body.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                    f'stroke="{color}" stroke-opacity="{opacity}" stroke-width="1" '
                    f'style="animation:crack{i} {GLITCH_CYCLE} step-end infinite"/>')
    return "\n".join(body), "\n".join(defs), css


def build(theme, glyphs, photo_uri, mask_uris, lids):
    colors = THEMES[theme]
    rnd = random.Random(SEED)
    drops, drop_css = drops_svg(colors, rnd)
    shards, shard_css = shards_svg(colors, rnd)
    name, tear_defs, name_css = name_svg(colors, rnd)
    half_points, closed_points = [], []
    for start in BLINK_STARTS:
        half_points.extend(((start, 0), (start + 0.5, 1),
                            (start + 2.3, 1), (start + 3.1, 0)))
        closed_points.extend(((start + 0.5, 0), (start + 1.0, 1),
                              (start + 1.7, 1), (start + 2.3, 0)))
    css = [
        "@keyframes camera {0%,100% {transform:scale(1) translate(0,0)} "
        "50% {transform:scale(1.03) translate(-4px,-2px)}}",
        "@keyframes breathe {0%,100% {transform:translateY(0)} "
        "42% {transform:translateY(var(--d))}}",
        ramp("lid-half", half_points),
        ramp("lid-closed", closed_points),
        "@keyframes scanmove {to {transform:translateY(18px)}}",
        "@keyframes accentPulse {0%,100% {transform:scaleX(1)} "
        "50% {transform:scaleX(.78)}}",
        frames("accentFill", f'fill:{colors["accent"]}',
               [(89.4, 92.4, f'fill:{colors["cp_red"]}')]),
        frames("flash", "opacity:0", [(90, 91.2, f'opacity:{colors["flash_op"]}')]),
        ".photo {transform-box:fill-box;transform-origin:55% 40%;"
        "animation:camera 18s ease-in-out infinite}",
        f".br {{animation:breathe {BREATH_DUR} cubic-bezier(.45,0,.55,1) infinite}}",
        f".lid-half {{animation:lid-half {BLINK_CYCLE} linear infinite}}",
        f".lid-closed {{animation:lid-closed {BLINK_CYCLE} linear infinite}}",
        ".scan {animation:scanmove 2.4s linear infinite}",
        ".gl,use[style*='silhouette'] {transform-origin:66px 125px;"
        "transform-box:view-box}",
        "@media (prefers-reduced-motion: reduce) {* {animation:none !important}}",
        *drop_css, *shard_css, *name_css,
    ]
    glyph = lambda key: escape(glyphs[key], quote=True)
    slices = "\n".join(
        f'<clipPath id="s{i}"><polygon points="'
        + " ".join(f"{p[j]},{p[j + 1]}" for j in range(0, 8, 2))
        + '"/></clipPath>' for i, p in enumerate(SLICES, 1))
    scanlines = "".join(f'<rect x="0" y="{y}" width="1200" height="2"/>'
                        for y in range(-18, 325, 18))
    mask_defs = "\n".join(
        f'<mask id="bm{k}" maskUnits="userSpaceOnUse" x="0" y="0" '
        f'width="700" height="458"><image href="{uri}" xlink:href="{uri}" '
        f'x="0" y="0" width="700" height="458" preserveAspectRatio="none"/></mask>'
        for k, uri in enumerate(mask_uris, 1))
    image = '<use href="#photo-img" xlink:href="#photo-img"/>'
    for k in range(1, BREATH_LAYERS + 1):
        image += (f'<g mask="url(#bm{k})"><g class="br" '
                  f'style="--d:-{number(BREATH_SHIFT * k / BREATH_LAYERS)}px">'
                  '<use href="#photo-img" xlink:href="#photo-img"/></g></g>')
    image += f'<g class="br" style="--d:-{number(BREATH_SHIFT)}px">'
    for kind in ("half", "closed"):
        uri = lids[kind]
        image += (f'<image class="lid lid-{kind}" href="{uri}" xlink:href="{uri}" '
                  f'x="300" y="98" width="160" height="44" opacity="0"/>')
    image += "</g>"
    tag_rects = ((66, 126, "tag_hackathons"), (204, 184, "tag_ship"),
                 (400, 122, "tag_vibe"))
    tags = "\n".join(
        f'<rect x="{x}" y="274" width="{width}" height="30" rx="4" '
        f'fill="{colors["tag_bg"]}" stroke="{colors["tag_stroke"]}"/>'
        f'<path d="{glyph(key)}" fill="{colors["tag_fill"][i]}"/>'
        for i, (x, width, key) in enumerate(tag_rects))
    soft = ('<filter id="soft"><feColorMatrix type="matrix" values="0.85 0 0 0 0.16  '
            '0 0.85 0 0 0.17  0 0 0.85 0 0.19  0 0 0 1 0"/></filter>'
            if theme == "light" else "")
    photo_filter = ' filter="url(#soft)"' if theme == "light" else ""
    label = "Ligreus - student developer, learning in public"
    if theme == "light":
        label += " (light)"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1200 340" width="1200" height="340" role="img" aria-label="{label}">
<defs>
<linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{colors["fade"]}" stop-opacity="1"/><stop offset="0.34" stop-color="{colors["fade"]}" stop-opacity="{colors["fade_mid"]}"/><stop offset="0.64" stop-color="{colors["fade"]}" stop-opacity="0"/></linearGradient>
<linearGradient id="vign" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{colors["fade"]}" stop-opacity="{colors["vign_top"]}"/><stop offset="0.32" stop-color="{colors["fade"]}" stop-opacity="0"/><stop offset="0.7" stop-color="{colors["fade"]}" stop-opacity="0"/><stop offset="1" stop-color="{colors["fade"]}" stop-opacity="{colors["vign_bottom"]}"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors["glass_a"]}" stop-opacity="{colors["glass_op"][0]}"/><stop offset="0.5" stop-color="{colors["glass_b"]}" stop-opacity="{colors["glass_op"][1]}"/><stop offset="1" stop-color="{colors["glass_a"]}" stop-opacity="{colors["glass_op"][2]}"/></linearGradient>
<linearGradient id="glass2" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{colors["glass2"]}" stop-opacity="{colors["glass2_op"][0]}"/><stop offset="1" stop-color="{colors["glass2"]}" stop-opacity="{colors["glass2_op"][1]}"/></linearGradient>
<radialGradient id="dropBody" cx="0.4" cy="0.35" r="0.65"><stop offset="0" stop-color="{colors["drop_core"]}" stop-opacity="0.05"/><stop offset="0.7" stop-color="{colors["drop_core"]}" stop-opacity="0.14"/><stop offset="1" stop-color="{colors["drop_rim"]}" stop-opacity="{colors["drop_rim_op"]}"/></radialGradient>
<linearGradient id="dropTrail" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{colors["drop_core"]}" stop-opacity="0"/><stop offset="1" stop-color="{colors["drop_core"]}" stop-opacity="{colors["trail_op"]}"/></linearGradient>
<g id="nm"><path d="{glyph("name")}"/></g>
{slices}
{tear_defs}
<linearGradient id="photoEdge" gradientUnits="userSpaceOnUse" x1="594" y1="0" x2="800" y2="0"><stop offset="0" stop-color="#000000"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
<mask id="photoFade" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="340"><rect x="0" y="0" width="1200" height="340" fill="url(#photoEdge)"/></mask>
<clipPath id="card"><rect x="0" y="0" width="1200" height="340" rx="16"/></clipPath>
<image id="photo-img" href="{photo_uri}" x="0" y="0" width="700" height="458"/>
{mask_defs}
{soft}
</defs>
<style>{" ".join(css)}</style>
<g clip-path="url(#card)">
<rect width="1200" height="340" fill="{colors["bg"]}"/>
<g mask="url(#photoFade)"{photo_filter}><g class="photo"><g transform="translate(600 -26.35) scale(0.914286)">{image}</g></g></g>
<rect x="0" y="0" width="1200" height="340" fill="{colors["overlay"]}" opacity="{colors["overlay_op"]}"/>
<rect x="0" y="0" width="1200" height="340" fill="url(#fadeL)"/>
<rect x="0" y="0" width="1200" height="340" fill="url(#vign)"/>
<g class="scan" fill="{colors["scan"]}" opacity="{colors["scan_op"]}">{scanlines}</g>
<g mask="url(#photoFade)">{drops}</g>
{shards}
<g>{name}</g>
<rect x="66" y="176" width="92" height="2" fill="{colors["accent"]}" opacity="0.8" style="transform-origin:66px 177px;transform-box:view-box;animation:accentPulse 6s ease-in-out infinite,accentFill {GLITCH_CYCLE} step-end infinite"/>
<rect x="166" y="176" width="238" height="2" fill="{colors["accent2"]}"/>
<path d="{glyph("tagline")}" fill="{colors["tagline"]}"/>
<path d="{glyph("stack")}" fill="{colors["stack"]}"/>
<g>{tags}</g>
<rect x="0" y="0" width="1200" height="340" fill="{colors["cp_red"]}" opacity="0" style="animation:flash {GLITCH_CYCLE} step-end infinite"/>
<rect x="0.5" y="0.5" width="1199" height="339" rx="16" fill="none" stroke="{colors["frame"]}"/>
</g>
</svg>
'''
    target = ROOT / "assets" / ("banner.svg" if theme == "dark" else "banner-light.svg")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg, encoding="utf-8", newline="\n")
    print(f"{target.relative_to(ROOT)}: {target.stat().st_size / 1024:.1f} КБ")


def main():
    photo_bytes = (HERE / "photo.jpg").read_bytes()
    photo = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
    if photo.size != PHOTO_SIZE:
        raise ValueError(f"Expected photo size {PHOTO_SIZE}, got {photo.size}")
    glyphs = json.loads((HERE / "glyphs.json").read_text(encoding="utf-8"))
    photo_uri = "data:image/jpeg;base64," + base64.b64encode(photo_bytes).decode("ascii")
    mask_uris = make_breath_masks()
    lids = make_lids(photo)
    for theme in THEMES:
        build(theme, glyphs, photo_uri, mask_uris, lids)


if __name__ == "__main__":
    main()
