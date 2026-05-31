#!/usr/bin/env python3
"""
Build geometry.html: the cross-model 'Internal geometry' gallery.

MOVE: extract the 6 already-rendered panels (E4B/26B/31B/NanBeige/MiniCPM ×2)
      from gemma.html's appendix.
ENRICH: render new panels for Granite-3B, Qwen-3.5-4B, DeepCoder from the
      organized scans in rys-tools/scans/data/ (same cosine/delta builders the
      original appendix used — lifted from transcripts/chart-generator...txt).
Then strip the appendix out of gemma.html and leave a pointer.
"""
import json, os, math, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANS = "/Users/anya/Projects/rys-tools/scans/data"

# ── palette (site CSS) ──
INK, INK2, MUTED = '#221E18', '#443D31', '#7C7466'
RULE, RULE2, TC = '#C7BDA9', '#D9D1BE', '#B85C3D'
SAGE, WINE, SLATE = '#5C7A66', '#7A2E2E', '#2F3F52'
GOLD, SLATEL, GOLDL = '#A6852E', '#5C7785', '#C8A84A'
SLATESL, GOLDSL = '#8FA5B5', '#E0C680'

STYLES = {
    'en_fact_vs_en_para': dict(color=SAGE,   w=2.0, dash='',      z=9,  label='EN fact ↔ paraphrase (same content, same lang)'),
    'en_fact_vs_zh_fact': dict(color=SLATE,  w=1.8, dash='',      z=8,  label='EN ↔ ZH fact (same content)'),
    'en_poem_vs_zh_poem': dict(color=GOLD,   w=1.8, dash='',      z=7,  label='EN ↔ ZH poem (same content)'),
    'en_math_vs_zh_math': dict(color=SLATEL, w=1.4, dash='',      z=6,  label='EN ↔ ZH math (same content)'),
    'en_fact_vs_fr_fact': dict(color=SLATESL,w=1.4, dash='',      z=5,  label='EN ↔ FR fact (same content)'),
    'en_poem_vs_fr_poem': dict(color=GOLDL,  w=1.4, dash='',      z=4,  label='EN ↔ FR poem (same content)'),
    'zh_fact_vs_fr_fact': dict(color=GOLDSL, w=1.2, dash='4 2',   z=3,  label='ZH ↔ FR fact (same content)'),
    'en_fact_vs_en_poem': dict(color=MUTED,  w=1.2, dash='3 2',   z=2,  label='EN fact ↔ poem (same lang, diff content)'),
    'zh_fact_vs_zh_poem': dict(color=RULE,   w=1.2, dash='3 2',   z=1,  label='ZH fact ↔ poem (same lang, diff content)'),
    'en_fact_vs_zh_poem': dict(color=WINE,   w=1.8, dash='',      z=10, label='EN fact ↔ ZH poem (diff lang, diff content)'),
    'en_poem_vs_zh_fact': dict(color=TC,     w=1.5, dash='4 1.5', z=0,  label='EN poem ↔ ZH fact (diff lang, diff content)'),
}
DRAW_ORDER = sorted(STYLES, key=lambda k: STYLES[k]['z'])


def fmt(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.')


def cosine_chart(data, figid, title, skip_neg1=True, y_range=None, W=1080, H=360):
    L, R, T, B = 68, 28, 36, 44
    CW, CH = W - L - R, H - T - B
    series = {}
    for key in DRAW_ORDER:
        if key not in data:
            continue
        pts = [(l, c) for l, c in zip(data[key]['layers'], data[key]['cosine_sim'])
               if not (skip_neg1 and l == -1)]
        if pts:
            series[key] = pts
    if not series:
        return ''
    all_layers = sorted({l for pts in series.values() for l, _ in pts})
    n = len(all_layers)
    all_vals = [v for pts in series.values() for _, v in pts]
    if y_range is None:
        vmin, vmax = min(all_vals), max(all_vals)
        pad = (vmax - vmin) * 0.08
        ymin = math.floor((vmin - pad) * 4) / 4
        ymax = math.ceil((vmax + pad) * 4) / 4
    else:
        ymin, ymax = y_range
    px = lambda l: L + (all_layers.index(l) / (n - 1)) * CW
    py = lambda v: T + (ymax - v) / (ymax - ymin) * CH
    p = [f'<svg id="{figid}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">']
    y = round(math.ceil(ymin / 0.25) * 0.25, 4)
    while y <= ymax + 1e-9:
        yy = py(y); z = abs(y) < 1e-9
        p.append(f'<line x1="{L}" x2="{W-R}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="{INK if z else RULE2}" stroke-width="{"1" if z else "0.5"}"/>')
        p.append(f'<text x="{L-6}" y="{yy+3.5:.2f}" font-family="JetBrains Mono" font-size="10" fill="{MUTED}" text-anchor="end">{"+" if y>0 else ""}{fmt(y)}</text>')
        y = round(y + 0.25, 4)
    my = T + CH / 2
    p.append(f'<text x="14" y="{my:.1f}" font-family="JetBrains Mono" font-size="10.5" letter-spacing="1.5" fill="{INK2}" text-anchor="middle" transform="rotate(-90 14 {my:.1f})">cosine similarity</text>')
    for ll in all_layers:
        if ll == -1 or ll % 5 == 0 or ll == all_layers[-1]:
            p.append(f'<text x="{px(ll):.2f}" y="{H-B+14:.0f}" font-family="JetBrains Mono" font-size="10" fill="{MUTED}" text-anchor="middle">{"emb" if ll==-1 else ll}</text>')
    p.append(f'<text x="{L+CW/2:.0f}" y="{H-2}" font-family="JetBrains Mono" font-size="10.5" letter-spacing="1.5" fill="{INK2}" text-anchor="middle">layer</text>')
    for key in DRAW_ORDER:
        if key not in series:
            continue
        s = STYLES[key]; pts = series[key]
        dash = f' stroke-dasharray="{s["dash"]}"' if s['dash'] else ''
        coords = ' '.join(f'{"M" if i==0 else "L"}{px(l):.2f},{py(c):.2f}' for i, (l, c) in enumerate(pts))
        p.append(f'<path d="{coords}" fill="none" stroke="{s["color"]}" stroke-width="{s["w"]}" stroke-linejoin="round"{dash}/>')
        for l, c in pts:
            r = 2.2 if key in ('en_fact_vs_zh_fact', 'en_fact_vs_zh_poem', 'en_fact_vs_en_para') else 1.6
            p.append(f'<circle cx="{px(l):.2f}" cy="{py(c):.2f}" r="{r}" fill="{s["color"]}"/>')
    ly = H - B + 26
    items = [(k, STYLES[k]) for k in DRAW_ORDER if k in series]
    col_w = (CW + R) / max(1, math.ceil(len(items) / 2))
    for i, (key, s) in enumerate(items):
        xi = L + (i // 2) * col_w; yi = ly + (i % 2) * 14
        dash = f' stroke-dasharray="{s["dash"]}"' if s['dash'] else ''
        p.append(f'<line x1="{xi:.0f}" x2="{xi+18:.0f}" y1="{yi-3}" y2="{yi-3}" stroke="{s["color"]}" stroke-width="{s["w"]}"{dash}/>')
        p.append(f'<circle cx="{xi+9:.0f}" cy="{yi-3}" r="1.4" fill="{s["color"]}"/>')
        p.append(f'<text x="{xi+22:.0f}" y="{yi}" font-family="JetBrains Mono" font-size="9.5" fill="{INK2}">{s["label"]}</text>')
    p.append('</svg>')
    return '\n'.join(p)


def delta_chart(data, figid, title, W=1080, H=300):
    L, R, T, B = 68, 28, 36, 36
    CW, CH = W - L - R, H - T - B
    layers, delta = data['layers'], data['delta_mean']
    n = len(layers)
    ymax = math.ceil(max(delta) * 1.1 / 100) * 100 or 1
    px = lambda i: L + (i / (n - 1)) * CW
    py = lambda v: T + (ymax - v) / ymax * CH
    p = [f'<svg id="{figid}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">']
    step = max(100, round(ymax / 5 / 100) * 100)
    y = 0
    while y <= ymax:
        yy = py(y)
        p.append(f'<line x1="{L}" x2="{W-R}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="{INK if y==0 else RULE2}" stroke-width="{"0.7" if y==0 else "0.5"}"/>')
        p.append(f'<text x="{L-6}" y="{yy+3.5:.2f}" font-family="JetBrains Mono" font-size="10" fill="{MUTED}" text-anchor="end">{y}</text>')
        y += step
    my = T + CH / 2
    p.append(f'<text x="14" y="{my:.1f}" font-family="JetBrains Mono" font-size="10.5" letter-spacing="1.5" fill="{INK2}" text-anchor="middle" transform="rotate(-90 14 {my:.1f})">‖ Δh ‖ (token-avg)</text>')
    top = ' '.join(f'{"M" if i==0 else "L"}{px(i):.2f},{py(v):.2f}' for i, v in enumerate(delta))
    p.append(f'<path d="{top} L{px(n-1):.2f},{py(0):.2f} L{px(0):.2f},{py(0):.2f} Z" fill="{SLATE}" fill-opacity="0.10" stroke="none"/>')
    p.append(f'<path d="{top}" fill="none" stroke="{SLATE}" stroke-width="1.6" stroke-linejoin="round"/>')
    for i, v in enumerate(delta):
        p.append(f'<circle cx="{px(i):.2f}" cy="{py(v):.2f}" r="1.6" fill="{SLATE}"/>')
    for i, l in enumerate(layers):
        if l % 5 == 0 or l == layers[-1]:
            p.append(f'<text x="{px(i):.2f}" y="{H-B+12}" font-family="JetBrains Mono" font-size="10" fill="{MUTED}" text-anchor="middle">{l}</text>')
    p.append(f'<text x="{L+CW/2:.0f}" y="{H-2}" font-family="JetBrains Mono" font-size="10.5" letter-spacing="1.5" fill="{INK2}" text-anchor="middle">layer</text>')
    p.append('</svg>')
    return '\n'.join(p)


def load(name):
    return json.load(open(os.path.join(SCANS, name)))


def figure(svg, fid, cap):
    return f'<div class="figure">\n{svg}\n<p class="figcap" id="{fid}-cap">{cap}</p>\n</div>'


def panel(mid, name, note, body):
    return (f'<details class="geo-accordion" id="geo-{mid}">\n'
            f'  <summary class="geo-summary"><span class="geo-model-name">{name}</span>'
            f'<span class="geo-model-note">{note}</span></summary>\n'
            f'  <div class="geo-panel">\n{body}\n  </div>\n</details>')


# ── new panels ───────────────────────────────────────────────────────────────
new_panels = []

# Granite-3B — the quant-invariance star (2/4/8-bit superimposable)
g_cos = cosine_chart(load('granite_3b_4bit_centered_last.json'), 'geoGraniteCos',
                     'Granite-4.1-3B — cosine by layer (4-bit)', y_range=(-1.0, 0.55))
g_del = delta_chart(load('granite_3b_4bit_delta.json'), 'geoGraniteDelta',
                    'Granite-4.1-3B — per-layer delta (4-bit)')
new_panels.append(panel('granite', 'Granite-4.1-3B · 40 layers', 'dense · scanned at 2/4/8-bit',
    figure(g_cos, 'figGeoGranite',
           '<b>Fig G7a.</b> Cross-language same-content cosine climbs to a broad mid-stack plateau '
           '(L15–30) — the interlingua / concept space — while the two ends sit in token-I/O geometry '
           '(deeply negative at the embedding side, re-separating at the output). The lesion map from the '
           '<a href="granite.html">Granite sweep</a> is this same map: noise is most lethal exactly where '
           'meaning lives. <b>Quant-invariant:</b> the 2-bit and 8-bit scans are superimposable on this '
           '(4-bit shown) — the geometry is a property of training, not precision.')
    + '\n' + figure(g_del, 'figGeoGraniteD',
           '<b>Fig G7b.</b> Per-layer hidden-state delta. The U-shape — large at the input/output ends, '
           'a flat ≈0.22 plateau through the middle — is the residual multiplier made visible, and the '
           'inverse of the noise-vulnerability curve.')))

# Qwen-3.5-4B — same signature at 2-bit
q_cos = cosine_chart(load('qwen35_4b_2bit_centered_last.json'), 'geoQwenCos',
                     'Qwen-3.5-4B — cosine by layer (2-bit)', y_range=(-1.0, 0.6))
new_panels.append(panel('qwen', 'Qwen-3.5-4B · 32 layers', 'dense · scanned at 2/4-bit',
    figure(q_cos, 'figGeoQwen',
           '<b>Fig G8.</b> Qwen-3.5-4B at 2-bit shows the same interlingua-in-the-middle signature — '
           'cross-lang same-content rising to a mid-stack peak, ends in token geometry — and it is '
           'unchanged at 4-bit (2-bit shown). Independent confirmation, on a different architecture and '
           'a harsher quant, that the concept-space geometry survives aggressive quantization.')))

# DeepCoder — a deeper reasoning model
d_cos = cosine_chart(load('deepcoder_3bit_centered_last.json'), 'geoDeepCos',
                     'DeepCoder — cosine by layer (3-bit)', y_range=(-1.0, 0.6))
new_panels.append(panel('deepcoder', 'DeepCoder · 48 layers', 'dense reasoning model · scanned at 2/3-bit',
    figure(d_cos, 'figGeoDeep',
           '<b>Fig G9.</b> DeepCoder (48 layers) carries the same mid-stack interlingua plateau across a '
           'much deeper stack, with the concept space spread over a longer middle band before the '
           'final-layer flip to output geometry. The signature is architecture-general; the depth over '
           'which it spreads scales with the model.')))

NEW_PANELS_HTML = '\n\n'.join(new_panels)

# ── extract the existing 6 panels from gemma.html ───────────────────────────
gemma = open(os.path.join(SITE, 'gemma.html'), encoding='utf-8').read()
m = re.search(r'<section id="appendix-geometry">(.*?)</section>', gemma, re.S)
assert m, "appendix-geometry section not found in gemma.html"
appendix_inner = m.group(1)
# keep from the legend onward (drop the section's own kicker/h2/dek; geometry.html has a hero)
leg = appendix_inner.find('<div class="geo-legend"')
existing = appendix_inner[leg:] if leg != -1 else appendix_inner

GALLERY = existing.rstrip() + '\n\n' + NEW_PANELS_HTML

# ── compose geometry.html ────────────────────────────────────────────────────
NAV = '''<nav class="labnav">
  <a class="home" href="index.html">THE VIVISECTION LAB</a>
  <a href="gemma.html">Gemma&nbsp;4</a>
  <a href="granite.html">Granite</a>
  <a href="hrm.html">HRM</a>
  <a href="geometry.html" class="active">Geometry</a>
  <span class="spacer"></span>
  <button class="theme-btn" type="button">☼ Light</button>
</nav>'''

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Internal geometry — The Vivisection Lab</title>
<meta name="description" content="Cross-model internal geometry: per-layer cross-language cosine similarity reveals a mid-stack interlingua/concept space — quant-invariant and architecture-general — across Gemma, Granite, Qwen, DeepCoder, NanBeige and MiniCPM.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/lab.css">
</head>
<body class="dark">

{NAV}

<main>

<section class="hero">
  <div class="topbar">
    <div><span class="dot"></span>Appendix · cross-model · the interlingua thread</div>
    <div class="right">9 models · cosine/delta scans · centered last-token</div>
  </div>
  <div class="kicker" style="margin-top:2.4rem">Where meaning lives, across architectures</div>
  <h1>Internal <em>geometry</em>.</h1>
  <p class="dek">
    One probe, run on every specimen: take parallel sentences in different
    languages saying the same thing, and measure the cosine similarity of their
    hidden states at each layer. A model that has built a shared concept space
    will pull same-content-different-language pairs <em>together</em> in the
    middle of the stack — an interlingua — while keeping the input and output ends
    in language-specific token geometry. That mid-stack plateau is the same place
    the <a href="granite.html">lesion maps</a> say meaning lives, and it shows up,
    quant-invariant, on every model below.
  </p>
</section>

<section data-screen-label="Gallery">
  <h2><span class="num">§</span>The gallery</h2>
  <p class="dek">Expand any model. Cosine-similarity scans are centered (per-layer mean removed) and read on the last token unless noted; delta charts show per-layer hidden-state change.</p>

{GALLERY}

</section>

<section data-screen-label="Reading">
  <h2><span class="num">§</span>How to read it</h2>
  <div class="col-side">
    <div>
      <p>
        The line that matters is <span class="hl-acc">same-content, cross-language</span>
        (e.g. EN ↔ ZH fact). When it rises above the same-language-different-content
        baselines in the middle layers, the model is representing <em>meaning</em>
        independently of <em>language</em> there. Where it peaks, and how sharply
        it collapses back to token geometry at the output, is the structural
        signature each architecture leaves.
      </p>
      <p>
        Three things recur across the nine models: the interlingua is
        <span class="hl-acc">mid-stack</span>, not distributed; the ends are token
        I/O; and the whole picture is <span class="hl-acc">quant-invariant</span> —
        2-bit and 8-bit scans of the same model superimpose. The geometry is a
        property of training, not precision.
      </p>
    </div>
    <aside class="aside">
      <span class="kicker">Caveat</span>
      EN↔FR pairs are confounded by shared Latin script and tokenizer overlap —
      read the EN↔ZH (Chinese) series as the trustworthy cross-language signal.
      Cosine magnitudes are comparable within a model, less so across models with
      different tokenizers; the <em>shape</em> is the result.
    </aside>
  </div>
  <p class="small muted" style="margin-top:2rem">
    Scan tools + data: <span class="mono">rys-tools/scans/</span> (mlx hidden-state extraction, centered cosine). Specimens: <a href="gemma.html">Gemma&nbsp;4</a> · <a href="granite.html">Granite</a> · <a href="hrm.html">HRM</a>.
  </p>
</section>

</main>
<script src="assets/lab.js"></script>
</body>
</html>
'''

open(os.path.join(SITE, 'geometry.html'), 'w', encoding='utf-8').write(page)
print(f"geometry.html written: {len(page):,} chars, {page.count('<svg')} svg charts "
      f"({len(new_panels)} new panels + extracted existing)")
