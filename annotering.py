"""Annotert prototype: hovedskisse med merkelapper, klammer og piler, og de andre
visningene ved siden av. Bygges som inline SVG (skarp tekst, prosjektets farger).
På mobil vises en enkel versjon: bildene under hverandre med en nummerert liste.

I innhold.json (alle koordinater i et lerret på 1000 bredde):
  "annotert": {
    "hoved": "bilder/…/skisse.svg",
    "topp": 130,                         # valgfri: hovedskissens y-posisjon
    "visninger": [{"fil": "…", "tittel": "Line Chart"}, …],
    "merker": [{"tittel": "…", "tekst": "…",
                "omrade": [x0, y0, x1, y1],      # andel av hovedskissen (0–1)
                "side": "left" | "top" | "right", # hvor klammen står
                "via": [[x, y]],                  # knekkpunkter for linjen
                "etikett": [x, y, bredde]}]       # merkelappens plassering
  }
"""
import re
from html import escape as e
from pathlib import Path
from urllib.parse import quote

ROT = Path(__file__).resolve().parent
B = 1000                       # lerretets bredde
HOVED = (20, 130, 600)         # x, y, bredde for hovedskissen
VISNING_X, VISNING_B = 670, 310
TEGN_PER_LINJE = 0.132         # ca. tegn per px ved 15,5 px tekst


def _forhold(sti):
    """Høyde/bredde fra SVG-filens egne mål."""
    hode = (ROT / sti).read_text(encoding="utf-8")[:400]
    m = re.search(r'width="([\d.]+)"\s+height="([\d.]+)"', hode)
    return float(m.group(2)) / float(m.group(1))


def _bryt(tekst, bredde):
    maks, linjer, linje = int(bredde * TEGN_PER_LINJE), [], ""
    for ord_ in tekst.split():
        if linje and len(linje) + 1 + len(ord_) > maks:
            linjer.append(linje)
            linje = ord_
        else:
            linje = f"{linje} {ord_}".strip()
    return linjer + ([linje] if linje else [])


def _etikett(m):
    x, y, b = m["etikett"]
    linjer = _bryt(m.get("tekst", ""), b - 32) if m.get("tekst") else []
    h = 50 + 21 * len(linjer) if linjer else 44
    tekst = f'<text class="ann-tittel" x="{x + 16}" y="{y + (29 if not linjer else 31)}">{e(m["tittel"])}</text>'
    tekst += "".join(f'<text class="ann-tekst" x="{x + 16}" y="{y + 56 + 21 * i}">{e(l)}</text>' for i, l in enumerate(linjer))
    return (x, y, b, h), f'<rect class="ann-boks" x="{x}" y="{y}" width="{b}" height="{h}" rx="10"/>{tekst}'


def _klamme_og_linje(m, hx, hy, hb, hh, boks, pil):
    x0, y0, x1, y1 = m["omrade"]
    X = lambda f: hx + hb * f
    Y = lambda f: hy + hh * f
    s = m.get("side", "left")
    if s == "top":
        by = Y(y0) - 8
        klamme = f"M{X(x0)} {by + 12} V{by} H{X(x1)} V{by + 12}"
        start = ((X(x0) + X(x1)) / 2, by)
    elif s == "right":
        bx = X(x1) + 10
        klamme = f"M{bx - 12} {Y(y0)} H{bx} V{Y(y1)} H{bx - 12}"
        start = (bx, (Y(y0) + Y(y1)) / 2)
    else:
        bx = X(x0) - 10
        klamme = f"M{bx + 12} {Y(y0)} H{bx} V{Y(y1)} H{bx + 12}"
        start = (bx, (Y(y0) + Y(y1)) / 2)

    punkter = [start] + [tuple(p) for p in m.get("via", [])]
    lx, ly, lb, lh = boks
    sx, sy = punkter[-1]
    if lx <= sx <= lx + lb:            # rett opp eller ned til merkelappen
        slutt = (sx, ly + lh + 6) if ly + lh < sy else (sx, ly - 6)
    else:                               # rett til siden
        slutt = (lx - 6, sy) if lx > sx else (lx + lb + 6, sy)
    punkter.append(slutt)
    linje = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in punkter)
    return (f'<path class="ann-klamme" d="{klamme}"/>'
            f'<path class="ann-linje" d="{linje}" marker-end="url(#{pil})"/>')


_antall = 0


def annotert(a):
    if not a:
        return ""
    global _antall
    _antall += 1
    pil = f"ann-pil-{_antall}"          # unik id når flere figurer står på siden
    hx, hy, hb = HOVED
    hy = a.get("topp", hy)            # flytt hovedskissen ned når merkelappene over trenger plass
    hh = hb * _forhold(a["hoved"])
    deler = [
        f'<defs><marker id="{pil}" class="ann-pil" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L8 5 L1 9"/></marker></defs>'
    ]

    # Visningene i en kolonne til høyre, litt vridd som ark på et bord (smalere når de er mange)
    visninger = a.get("visninger", [])
    vx, vb = (VISNING_X, VISNING_B) if len(visninger) <= 3 else (740, 240)
    y, hoyest = 20, hy + hh
    for i, v in enumerate(visninger):
        h = vb * _forhold(v["fil"])
        vri = (-2, 1.5, -1.5)[i % 3]
        cx, cy = vx + vb / 2, y + h / 2
        deler.append(f'<image class="ann-ark" href="{e(quote(v["fil"]))}" x="{vx}" y="{y:.1f}" '
                     f'width="{vb}" height="{h:.1f}" transform="rotate({vri} {cx:.1f} {cy:.1f})"/>')
        bredde = 30 + 10 * len(v["tittel"])
        deler.append(f'<rect class="ann-boks" x="{vx - 14}" y="{y + 12:.1f}" width="{bredde:.0f}" height="40" rx="10"/>'
                     f'<text class="ann-tittel" x="{vx + 1}" y="{y + 38:.1f}">{e(v["tittel"])}</text>')
        y += h + 16
        hoyest = max(hoyest, y)

    deler.append(f'<image class="ann-ark" href="{e(quote(a["hoved"]))}" x="{hx}" y="{hy}" width="{hb}" height="{hh:.1f}"/>')

    for m in a.get("merker", []):
        boks, etikett = _etikett(m)
        deler.append(_klamme_og_linje(m, hx, hy, hb, hh, boks, pil))
        deler.append(etikett)
        hoyest = max(hoyest, boks[1] + boks[3] + 10)

    svg = (f'<svg class="annotert-stor" viewBox="0 0 {B} {hoyest:.0f}" role="img" '
           f'aria-label="Annotated sketches of the prototype">{"".join(deler)}</svg>')

    # Mobil: hovedskissen, nummererte forklaringer og visningene under hverandre
    liste = ""
    for m in a.get("merker", []):
        tekst = f'<span>{e(m["tekst"])}</span>' if m.get("tekst") else ""
        liste += f'<li><strong>{e(m["tittel"])}</strong>{tekst}</li>'
    visninger = "".join(
        f'<figure><img src="{e(quote(v["fil"]))}" alt="{e(v["tittel"])}" loading="lazy"><figcaption>{e(v["tittel"])}</figcaption></figure>'
        for v in a.get("visninger", [])
    )
    prikker = ""
    for i, m in enumerate(a.get("merker", []), 1):
        x0, y0, x1, y1 = m["omrade"]
        s = m.get("side", "left")
        x, y = {"top": ((x0 + x1) / 2, y0), "right": (x1, (y0 + y1) / 2)}.get(s, (x0, (y0 + y1) / 2))
        prikker += f'<span class="ann-prikk" style="left:{x * 100:.1f}%;top:{y * 100:.1f}%">{i}</span>'
    mobil = (f'<div class="annotert-liten"><div class="ann-hoved"><img src="{e(quote(a["hoved"]))}" '
             f'alt="Main view of the prototype" loading="lazy">{prikker}</div>'
             f'<ol class="ann-liste">{liste}</ol><div class="ann-visninger">{visninger}</div></div>')
    return f'<div class="annotert">{svg}{mobil}</div>'
