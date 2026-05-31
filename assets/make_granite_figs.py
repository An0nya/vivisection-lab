#!/usr/bin/env python3
"""
Generate the two data-driven granite SVG figures for the vivisection site,
styled to match the existing Gemma 'Surgical Record' page (light palette;
the page applies a CSS invert filter for dark mode, so author in light).

Reads:  /Users/anya/Projects/rys-tools/granite/results/granite_mlx_sweep_results.jsonl
Writes: granite_layermap.svg, granite_dose.svg  (next to this script)
"""
import json, collections, math, statistics as st, os

DATA = "/Users/anya/Projects/rys-tools/granite/results/granite_mlx_sweep_results.jsonl"
OUT = os.path.dirname(os.path.abspath(__file__))

# palette (matches index.html :root)
INK, MUTED, RULE = "#221E18", "#7C7466", "#C7BDA9"
TERRA, SAGE, WINE, GOLD = "#B85C3D", "#5C7A66", "#7A2E2E", "#A6852E"
PAPER, BG = "#F6F2E9", "#EFEAE0"
MONO = "'JetBrains Mono', ui-monospace, monospace"
SERIF = "'Newsreader', Georgia, serif"

# ---- load + per-domain paired-t (same method as analyze_overnight.py) ----
cell = {}
dom_probes = collections.defaultdict(set)
for line in open(DATA):
    line = line.strip()
    if not line:
        continue
    d = json.loads(line)
    cell[(d["config_id"], d["probe"], d["seed"])] = d["score"]
    gt = d["grader_type"]
    dom = "math" if gt == "math" else ("eq" if gt == "eq_sketch" else "mc")
    dom_probes[dom].add(d["probe"])


def paired(cfg, probes):
    diffs, vals = [], []
    for p in probes:
        for s in range(15):
            kb, kc = ("baseline", p, s), (cfg, p, s)
            if kb in cell and kc in cell:
                diffs.append(cell[kc] - cell[kb]); vals.append(cell[kc])
    if not diffs:
        return None
    n = len(diffs); md = sum(diffs) / n
    if len(set(diffs)) > 1:
        sd = st.stdev(diffs); t = md / (sd / math.sqrt(n)) if sd else 0.0
    else:
        t = 0.0 if md == 0 else (8.0 if md > 0 else -8.0)
    return dict(mean=sum(vals) / n, t=max(-12, min(12, t)))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=11, fill=INK, anchor="start", family=MONO, weight=400, style="normal", ls=None):
    extra = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}"{extra}>{esc(s)}</text>')


# ============================ FIG 1: LAYER MAP ============================
def layer_map():
    W, H = 940, 560
    L, R, TOP = 76, 28, 120
    plot_w = W - L - R
    n = 40
    step = plot_w / n
    bw = step * 0.62

    dup_eq = [paired(f"dup_{i}", dom_probes["eq"]) for i in range(n)]
    prune_eq = [paired(f"prune_{i}", dom_probes["eq"]) for i in range(n)]
    dup_mc = [paired(f"dup_{i}", dom_probes["mc"]) for i in range(n)]
    prune_mc = [paired(f"prune_{i}", dom_probes["mc"]) for i in range(n)]

    # two panels: dup-eq (top), prune-eq (bottom), shared zero line in middle
    panel_h = 175
    midgap = 46
    yA0 = TOP + panel_h          # zero line of top panel (bars go up)
    yB0 = yA0 + midgap            # zero line of bottom panel (bars go down)
    tmax = 10.0

    def bar_h(t):
        return (min(abs(t), tmax) / tmax) * panel_h

    s = []
    s.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img">')
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')
    # titles
    s.append(txt(L, 28, "THE GRANITE LAYER MAP", 13, INK, weight=600, ls="0.12em"))
    s.append(txt(L, 46, "duplicate / prune each of 40 layers → effect on emotional-reasoning (EQ), paired t vs baseline", 11, MUTED))
    # rotated left-axis labels for the two panels
    cyA = (TOP + yA0) / 2
    cyB = yB0 + panel_h / 2.4
    s.append(f'<text x="20" y="{cyA:.1f}" font-family="{MONO}" font-size="10.5" fill="{INK}" font-weight="600" text-anchor="middle" letter-spacing="0.1em" transform="rotate(-90 20 {cyA:.1f})">DUPLICATE ▲ EQ↑</text>')
    s.append(f'<text x="20" y="{cyB:.1f}" font-family="{MONO}" font-size="10.5" fill="{INK}" font-weight="600" text-anchor="middle" letter-spacing="0.1em" transform="rotate(-90 20 {cyB:.1f})">PRUNE ▲ EQ↑</text>')

    # gridlines at t=5 and t=10
    for tv in (5, 10):
        yh = bar_h(tv)
        for (y0, sgn) in ((yA0, -1), (yB0, 1)):
            yy = y0 + sgn * yh
            s.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="{RULE}" stroke-width="0.6" stroke-dasharray="2 4"/>')
        s.append(txt(L - 6, yA0 - yh + 3, f"t={tv}", 9, MUTED, anchor="end"))
        s.append(txt(L - 6, yB0 + yh + 3, f"t={tv}", 9, MUTED, anchor="end"))
    # zero lines
    s.append(f'<line x1="{L}" y1="{yA0}" x2="{W-R}" y2="{yA0}" stroke="{INK}" stroke-width="1"/>')
    s.append(f'<line x1="{L}" y1="{yB0}" x2="{W-R}" y2="{yB0}" stroke="{INK}" stroke-width="1"/>')

    for i in range(n):
        cx = L + step * i + step / 2
        # ---- top: dup eq ----
        de = dup_eq[i]
        if de:
            t = de["t"]
            h = bar_h(t)
            mc = dup_mc[i]["mean"] if dup_mc[i] else 1.0
            # color: sage if boost; wine if hurts; gold edge if mc cost
            col = SAGE if t > 0 else WINE
            if t > 0:
                y = yA0 - h
                s.append(f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}" opacity="{0.55+0.4*min(abs(t)/tmax,1):.2f}"/>')
                # mc-cost marker: a small gold/wine cap if dup dents mc
                if mc < 0.995:
                    capc = WINE if mc < 0.9 else GOLD
                    s.append(f'<rect x="{cx-bw/2:.1f}" y="{y-3:.1f}" width="{bw:.1f}" height="3" fill="{capc}"/>')
            else:
                s.append(f'<rect x="{cx-bw/2:.1f}" y="{yA0:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}" opacity="0.5"/>')
        # ---- bottom: prune eq ----
        pe = prune_eq[i]
        if pe:
            t = pe["t"]
            h = bar_h(t)
            col = SAGE if t > 0 else WINE
            if t > 0:
                s.append(f'<rect x="{cx-bw/2:.1f}" y="{yB0:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}" opacity="{0.55+0.4*min(abs(t)/tmax,1):.2f}"/>')
            else:
                s.append(f'<rect x="{cx-bw/2:.1f}" y="{yB0-h:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}" opacity="0.5"/>')
    # x-axis layer ticks (below bottom panel)
    for i in range(0, n, 2):
        cx = L + step * i + step / 2
        s.append(txt(cx, H - 84, str(i), 8.5, MUTED, anchor="middle"))
    s.append(txt(L + plot_w / 2, H - 66, "layer index  (0 = embedding side  →  39 = output side)", 10, MUTED, anchor="middle"))

    # annotations for landmark layers — staggered heights, guide line starts below label
    def annot(i, label, col, ylab, anchor="middle"):
        cx = L + step * i + step / 2
        s.append(f'<line x1="{cx:.1f}" y1="{ylab+5:.1f}" x2="{cx:.1f}" y2="{yB0+panel_h:.1f}" stroke="{col}" stroke-width="0.7" stroke-dasharray="1 3" opacity="0.55"/>')
        tx = cx + (6 if anchor == "start" else -6 if anchor == "end" else 0)
        s.append(txt(tx, ylab, label, 9.5, col, anchor=anchor, weight=600))

    annot(6, "L6 ✕ retrieval bottleneck", WINE, 70, anchor="start")
    annot(10, "L10 ★ EQ champion", SAGE, 90, anchor="start")
    annot(33, "L33 — EQ-for-MC cost", GOLD, 70, anchor="middle")
    annot(39, "L39 ✕ output", WINE, 90, anchor="end")

    # legend
    ly = H - 38
    items = [(SAGE, "EQ boost"), (WINE, "EQ / model damage"), (GOLD, "+ dents MC (factual recall)")]
    lx = L
    for col, lab in items:
        s.append(f'<rect x="{lx}" y="{ly-9}" width="11" height="11" fill="{col}"/>')
        s.append(txt(lx + 16, ly, lab, 10, INK))
        lx += 12 + 9 * len(lab) + 26
    s.append('</svg>')
    open(os.path.join(OUT, "granite_layermap.svg"), "w").write("\n".join(s))
    print("wrote granite_layermap.svg")


# ============================ FIG 2: DOSE-RESPONSE ============================
def dose():
    W, H = 940, 500
    L, R, TOP, BOT = 64, 150, 64, 64
    pw, ph = W - L - R, H - TOP - BOT
    layers = [5, 10, 17, 24, 33, 38]
    colors = {5: GOLD, 10: SAGE, 17: TERRA, 24: "#2F3F52", 33: WINE, 38: "#9A6BA0"}
    xs = [2, 3, 4, 5, 6, 8]
    xmin, xmax = 2, 8

    def X(k):
        return L + (k - xmin) / (xmax - xmin) * pw

    def Y(v):
        return TOP + (1 - v / 0.8) * ph

    # gather curves
    curves = {}
    for Lr in layers:
        pts = {2: paired(f"dup_{Lr}", dom_probes["eq"])}
        for k in [3, 4, 5, 6, 8]:
            r = paired(f"dose_{Lr}_x{k}", dom_probes["eq"])
            if r:
                pts[k] = r
        curves[Lr] = pts

    base_eq = sum(cell[("baseline", p, s)] for p in dom_probes["eq"] for s in range(15) if ("baseline", p, s) in cell)
    base_n = sum(1 for p in dom_probes["eq"] for s in range(15) if ("baseline", p, s) in cell)
    base_eq /= base_n

    s = []
    s.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img">')
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')
    s.append(txt(L, 28, "DOSE–RESPONSE: HOW MANY COPIES?", 13, INK, weight=600, ls="0.12em"))
    s.append(txt(L, 46, "stacking N copies of one EQ-winner layer — EQ score vs copy count", 11, MUTED))

    # therapeutic / overdose shading
    s.append(f'<rect x="{X(2)-14:.1f}" y="{TOP}" width="{X(3)-X(2)+14:.1f}" height="{ph}" fill="{SAGE}" opacity="0.06"/>')
    s.append(f'<rect x="{X(4):.1f}" y="{TOP}" width="{X(xmax)-X(4)+10:.1f}" height="{ph}" fill="{WINE}" opacity="0.06"/>')
    s.append(txt((X(2)+X(3))/2, TOP+14, "therapeutic", 9.5, SAGE, anchor="middle", style="italic"))
    s.append(txt((X(4)+X(8))/2, TOP+14, "overdose → collapse", 9.5, WINE, anchor="middle", style="italic"))

    # y grid
    for v in [0, 0.2, 0.4, 0.6, 0.8]:
        yy = Y(v)
        s.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        s.append(txt(L - 8, yy + 3, f"{v:.1f}", 9, MUTED, anchor="end"))
    s.append(txt(L - 8, TOP - 10, "EQ", 9.5, MUTED, anchor="end"))
    # baseline line
    yb = Y(base_eq)
    s.append(f'<line x1="{L}" y1="{yb:.1f}" x2="{W-R}" y2="{yb:.1f}" stroke="{INK}" stroke-width="0.8" stroke-dasharray="4 3"/>')
    s.append(txt(W - R + 6, yb + 3, f"baseline {base_eq:.2f}", 9, MUTED))

    # x ticks
    for k in xs:
        s.append(f'<line x1="{X(k):.1f}" y1="{TOP}" x2="{X(k):.1f}" y2="{TOP+ph}" stroke="{RULE}" stroke-width="0.4" stroke-dasharray="1 4"/>')
        s.append(txt(X(k), TOP + ph + 18, f"×{k}", 11, INK, anchor="middle", weight=600))
    s.append(txt(L + pw / 2, H - 22, "number of copies of the layer (×2 = one extra / a single dup)", 10, MUTED, anchor="middle"))

    # curves
    labels = []  # (y_target, col, text)
    for Lr in layers:
        col = colors[Lr]
        pts = curves[Lr]
        ks = sorted(pts)
        path = []
        for j, k in enumerate(ks):
            x, y = X(k), Y(pts[k]["mean"])
            path.append(("M" if j == 0 else "L") + f"{x:.1f},{y:.1f}")
        s.append(f'<path d="{" ".join(path)}" fill="none" stroke="{col}" stroke-width="2.2" opacity="0.9"/>')
        for k in ks:
            x, y = X(k), Y(pts[k]["mean"])
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}"/>')
        labels.append([Y(pts[2]["mean"]) + 3, col, f"L{Lr}  {pts[2]['mean']:.2f}"])
    # de-collide right-edge labels (min 15px apart)
    labels.sort()
    for j in range(1, len(labels)):
        if labels[j][0] - labels[j - 1][0] < 15:
            labels[j][0] = labels[j - 1][0] + 15
    for y, col, t in labels:
        s.append(txt(W - R + 10, y, t, 11, col, weight=600))
    # callout: L24 exception
    x24, y24 = X(3), Y(curves[24][3]["mean"])
    s.append(f'<circle cx="{x24:.1f}" cy="{y24:.1f}" r="6" fill="none" stroke="#2F3F52" stroke-width="1.4"/>')
    s.append(txt(x24 + 10, y24 - 8, "L24: ×3 beats ×2", 9.5, "#2F3F52", style="italic"))
    s.append('</svg>')
    open(os.path.join(OUT, "granite_dose.svg"), "w").write("\n".join(s))
    print("wrote granite_dose.svg")


layer_map()
dose()
print("done ->", OUT)
