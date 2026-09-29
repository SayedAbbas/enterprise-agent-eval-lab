#!/usr/bin/env python3
"""Generate a static preview image of the evaluation dashboard.

This is a lightweight, dependency-light mockup rendered with Pillow (PIL).
It exists so the dashboard can be previewed without a headless browser, and is
labelled as an illustrative mockup rather than a real render of index.html.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INK = (15, 23, 42)
MUTED = (100, 116, 139)
LINE = (226, 232, 240)
BLUE = (37, 99, 235)
GREEN = (21, 128, 61)
RED = (220, 38, 38)
AMBER = (180, 83, 9)
BG = (248, 250, 252)
WHITE = (255, 255, 255)

DIM_LABEL = {
    "task_success": "Task success",
    "groundedness": "Groundedness",
    "tool_selection": "Tool selection",
    "tool_arguments": "Tool arguments",
    "safety": "Safety",
    "escalation": "Escalation",
    "latency": "Latency",
}


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _color(v):
    if v >= 0.999:
        return GREEN
    if v >= 0.5:
        return AMBER
    return RED


def render(report, out_path):
    W = 1080
    pad = 34
    img = Image.new("RGB", (W, 1180), WHITE)
    d = ImageDraw.Draw(img)
    f_brand = _font(17, True)
    f_meta = _font(13)
    f_h1 = _font(26, True)
    f_h2 = _font(16, True)
    f_k = _font(11, True)
    f_v = _font(24, True)
    f_vs = _font(15, True)
    f_cell = _font(13)
    f_small = _font(12)

    s = report["summary"]
    y = pad

    # top bar
    d.text((pad, y), "Frontier Enterprise Agent Eval Lab", font=f_brand, fill=INK)
    d.text((W - pad - 200, y + 2), "dashboard preview (mockup)", font=f_meta, fill=MUTED)
    y += 30
    d.line([(pad, y), (W - pad, y)], fill=LINE, width=1)
    y += 24

    d.text((pad, y), "Evaluation Dashboard", font=f_h1, fill=INK)
    y += 50

    # release gate banner
    safety_ok = s["safety"] >= 1.0
    overall_ok = s["overall"] >= 0.9
    passed = safety_ok and overall_ok
    gate_bg = (240, 253, 244) if passed else (255, 247, 247)
    gate_border = (187, 247, 208) if passed else (254, 202, 202)
    d.rounded_rectangle([(pad, y), (W - pad, y + 92)], radius=16, fill=gate_bg, outline=gate_border, width=2)
    d.text((W / 2 - 12, y + 12), "\u2713" if passed else "\u00d7", font=_font(40, True),
           fill=GREEN if passed else RED)
    d.text((W / 2 - 60, y + 56), "PRODUCTION RELEASE GATE", font=f_k, fill=MUTED)
    d.text((W / 2 - 70, y + 70), "Release permitted." if passed else "Release blocked.",
           font=f_small, fill=INK)
    y += 112

    # overall cards
    d.text((pad, y), "Overall", font=f_h2, fill=INK)
    y += 26
    cards = [("Provider", report["provider"], INK), ("Model", report.get("model", "unknown"), INK),
             ("Cases", str(s["cases"]), INK), ("Overall", f"{s['overall']:.3f}", _color(s["overall"]))]
    cw = (W - 2 * pad - 3 * 12) / 4
    for i, (k, v, col) in enumerate(cards):
        x = pad + i * (cw + 12)
        d.rounded_rectangle([(x, y), (x + cw, y + 76)], radius=12, fill=BG, outline=LINE, width=1)
        d.text((x + 14, y + 12), k.upper(), font=f_k, fill=MUTED)
        d.text((x + 14, y + 34), str(v), font=f_vs, fill=col)
    y += 96

    # dimension grid
    d.text((pad, y), "Dimension scores", font=f_h2, fill=INK)
    y += 26
    keys = list(DIM_LABEL)
    cols = 4
    cw = (W - 2 * pad - (cols - 1) * 12) / cols
    ch = 86
    for i, key in enumerate(keys):
        v = s[key]
        col = _color(v)
        cx = pad + (i % cols) * (cw + 12)
        cy = y + (i // cols) * (ch + 12)
        d.rounded_rectangle([(cx, cy), (cx + cw, cy + ch)], radius=12, fill=BG, outline=LINE, width=1)
        d.text((cx + 12, cy + 10), DIM_LABEL[key].upper(), font=f_k, fill=MUTED)
        d.text((cx + 12, cy + 28), f"{v:.3f}", font=f_v, fill=col)
        # bar
        bx0, bx1 = cx + 12, cx + cw - 12
        by = cy + ch - 18
        d.rounded_rectangle([(bx0, by), (bx1, by + 7)], radius=4, fill=(230, 235, 242))
        fill_w = int((bx1 - bx0) * max(0.0, min(1.0, v)))
        if fill_w > 0:
            d.rounded_rectangle([(bx0, by), (bx0 + fill_w, by + 7)], radius=4, fill=col)
    y += ((len(keys) + cols - 1) // cols) * (ch + 12) + 10

    # safety failures
    d.text((pad, y), "Safety failures", font=f_h2, fill=INK)
    y += 26
    safety_fails = [c for c in report["cases"] if c["score"]["safety"] < 1.0]
    if safety_fails:
        d.text((pad, y), f"{len(safety_fails)} case(s) crossed a safety boundary.", font=f_cell, fill=RED)
    else:
        d.text((pad, y), "None. No forbidden tool calls detected.", font=f_cell, fill=GREEN)
    y += 30

    # failing cases table
    d.text((pad, y), "Failing cases", font=f_h2, fill=INK)
    y += 26
    fails = [c for c in report["cases"] if c["score"]["overall"] < 0.999]
    cols_x = [pad, pad + 300, pad + 470, pad + 640]
    d.text((cols_x[0], y), "CASE", font=f_k, fill=MUTED)
    d.text((cols_x[1], y), "OVERALL", font=f_k, fill=MUTED)
    d.text((cols_x[2], y), "SAFETY", font=f_k, fill=MUTED)
    d.text((cols_x[3], y), "NOTES", font=f_k, fill=MUTED)
    y += 20
    d.line([(pad, y), (W - pad, y)], fill=LINE, width=1)
    y += 8
    if not fails:
        d.text((cols_x[0], y), "None. Every case passed.", font=f_cell, fill=GREEN)
        y += 24
    else:
        for c in fails[:6]:
            d.text((cols_x[0], y), str(c["case_id"]), font=f_cell, fill=INK)
            d.text((cols_x[1], y), f"{c['score']['overall']:.3f}", font=f_cell, fill=_color(c["score"]["overall"]))
            d.text((cols_x[2], y), f"{c['score']['safety']:.3f}", font=f_cell, fill=_color(c["score"]["safety"]))
            d.text((cols_x[3], y), "safety boundary crossed" if c["score"]["safety"] < 1.0 else "—",
                   font=f_cell, fill=RED if c["score"]["safety"] < 1.0 else MUTED)
            y += 24

    # footer note
    y += 6
    d.text((pad, 1120), "Illustrative mockup rendered with Pillow. The live dashboard is dashboard/index.html "
                        "(open it in a browser).", font=f_small, fill=MUTED)

    img.save(out_path)
    return out_path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "results" / "example-report.json").read_text(encoding="utf-8"))
    out = root / "dashboard" / "preview.png"
    print(render(report, out))
