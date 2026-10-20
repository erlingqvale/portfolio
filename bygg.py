#!/usr/bin/env python3
"""Bygger nettsiden og portefolje-kort.pdf fra innhold.json.

Bruk:  python3 bygg.py
Lager index.html, én side per prosjekt i prosjekter/, og PDF-en
(via Google Chrome i headless-modus).
"""
import json
import shutil
import subprocess
import sys
from html import escape as e
from pathlib import Path

ROT = Path(__file__).resolve().parent
CHROME_KANDIDATER = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
]


def les_innhold():
    return json.loads((ROT / "innhold.json").read_text(encoding="utf-8"))


def meta(p):
    return " · ".join(e(x) for x in [p.get("aar"), p.get("rolle")] if x)


def lenker(k):
    deler = []
    if k.get("epost"):
        deler.append(f'<a href="mailto:{e(k["epost"])}">{e(k["epost"])}</a>')
    if k.get("telefon"):
        tlf = k["telefon"].replace(" ", "")
        deler.append(f'<a href="tel:{e(tlf)}">{e(k["telefon"])}</a>')
    if k.get("linkedin"):
        deler.append(f'<a href="{e(k["linkedin"])}">LinkedIn</a>')
    if k.get("github"):
        deler.append(f'<a href="{e(k["github"])}">GitHub</a>')
    return deler


def stikkord(liste, klasse="stikkord"):
    return f'<ul class="{klasse}">{"".join(f"<li>{e(s)}</li>" for s in liste)}</ul>'


def side(tittel, beskrivelse, kropp, css="stil.css"):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(tittel)}</title>
<meta name="description" content="{e(beskrivelse)}">
<link rel="stylesheet" href="{css}">
</head>
<body>
{kropp}
</body>
</html>
"""


def bunntekst(d):
    k = d["kontakt"]
    return f'<footer class="bredde"><p>{" · ".join(lenker(k))}</p></footer>'


def prosjektkort(p):
    bilde = f'<img src="{e(p["bilde"])}" alt="" loading="lazy">' if p.get("bilde") else ""
    return f"""
      <a class="kort" href="prosjekter/{e(p["slug"])}.html">
        {bilde}
        <div class="meta">{meta(p)}</div>
        <h3>{e(p["tittel"])}</h3>
        <p>{e(p.get("kort", ""))}</p>
        {stikkord(p.get("stikkord", []))}
        <span class="mer">Read the case →</span>
      </a>"""


def lag_forside(d):
    kropp = f"""<header class="topp">
  <div class="bredde">
    <p class="overtittel">Portfolio</p>
    <h1>{e(d["navn"])}</h1>
    <p class="tittel">{e(d["tittel"])}</p>
    <p class="ingress">{e(d["ingress"])}</p>
    <nav class="kontakt">{" · ".join(lenker(d["kontakt"]))}</nav>
  </div>
</header>
<main class="bredde">
  <section id="prosjekter">
    <h2>Projects</h2>
    <div class="rutenett">{"".join(prosjektkort(p) for p in d["prosjekter"])}
    </div>
  </section>
  <section id="ferdigheter">
    <h2>Skills &amp; tools</h2>
    {stikkord(d["ferdigheter"], "stikkord stor")}
  </section>
</main>
{bunntekst(d)}"""
    return side(f'{d["navn"]} – Portfolio', d["ingress"], kropp)


def blokker(rader, klasse):
    return "".join(
        f'<div class="{klasse}"><h3>{e(r["tittel"])}</h3><p>{e(r["tekst"])}</p></div>'
        for r in rader
    )


def lag_prosjektside(d, p, forrige, neste):
    bilde = f'<img class="hovedbilde" src="../{e(p["bilde"])}" alt="">' if p.get("bilde") else ""
    losning = (
        f'<section><h2>The solution</h2><div class="rutenett">{blokker(p["losning"], "kort")}</div></section>'
        if p.get("losning") else ""
    )
    prosess = (
        f'<section><h2>The process</h2><ol class="prosess">'
        + "".join(f'<li><h3>{e(s["tittel"])}</h3><p>{e(s["tekst"])}</p></li>' for s in p["prosess"])
        + "</ol></section>"
        if p.get("prosess") else ""
    )
    lenke = f'<p><a class="mer" href="{e(p["lenke"])}">View project →</a></p>' if p.get("lenke") else ""
    kropp = f"""<header class="topp smal">
  <div class="bredde">
    <p class="overtittel"><a href="../index.html">← {e(d["navn"])}</a></p>
    <h1>{e(p["tittel"])}</h1>
    <p class="tittel">{meta(p)}</p>
    <p class="ingress">{e(p.get("kort", ""))}</p>
    {stikkord(p.get("stikkord", []))}
  </div>
</header>
<main class="bredde">
  {bilde}
  <section><h2>The challenge</h2><p class="tekst">{e(p.get("utfordring", ""))}</p>{lenke}</section>
  {losning}
  {prosess}
  <nav class="bla">
    <a href="{e(forrige["slug"])}.html">← {e(forrige["tittel"])}</a>
    <a href="{e(neste["slug"])}.html">{e(neste["tittel"])} →</a>
  </nav>
</main>
{bunntekst(d)}"""
    return side(f'{p["tittel"]} – {d["navn"]}', p.get("kort", ""), kropp, "../stil.css")


def lag_pdf_html(d):
    """Kortversjon: én A4-side med det viktigste."""
    k = d["kontakt"]
    kontaktlinje = " · ".join(
        x for x in [k.get("epost"), k.get("telefon"), k.get("sted"), k.get("linkedin"), k.get("github")] if x
    )
    prosjekter = "".join(
        f"""
      <div class="p">
        <div class="ph"><strong>{e(p["tittel"])}</strong><span>{meta(p)}</span></div>
        <p>{e(p.get("kort", ""))}</p>
      </div>"""
        for p in d["prosjekter"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 16mm 16mm 14mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font: 9.5pt/1.45 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #1c2430; margin: 0; }}
  h1 {{ font-size: 22pt; margin: 0; letter-spacing: -0.02em; }}
  .tittel {{ color: #2a5bd7; font-weight: 600; margin: 2pt 0 4pt; font-size: 11pt; }}
  .kontakt {{ color: #5b6573; font-size: 8.5pt; }}
  .ingress {{ margin: 8pt 0 0; font-size: 10pt; }}
  hr {{ border: 0; border-top: 1.5pt solid #2a5bd7; margin: 10pt 0; width: 40pt; }}
  h2 {{ font-size: 9pt; text-transform: uppercase; letter-spacing: 0.1em; color: #5b6573; margin: 12pt 0 6pt; }}
  .p {{ margin-bottom: 7pt; break-inside: avoid; }}
  .ph {{ display: flex; justify-content: space-between; gap: 8pt; }}
  .ph span {{ color: #5b6573; font-size: 8.5pt; white-space: nowrap; }}
  .p p {{ margin: 1pt 0 0; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  .ferd {{ display: flex; flex-wrap: wrap; gap: 4pt; }}
  .ferd li {{ background: #eef2fb; color: #1e3f99; padding: 1.5pt 6pt; border-radius: 8pt; font-size: 8.5pt; }}
</style></head>
<body>
  <h1>{e(d["navn"])}</h1>
  <div class="tittel">{e(d["tittel"])}</div>
  <div class="kontakt">{e(kontaktlinje)}</div>
  <p class="ingress">{e(d["ingress"])}</p>
  <hr>
  <h2>Projects</h2>{prosjekter}
  <h2>Skills &amp; tools</h2><ul class="ferd">{"".join(f"<li>{e(f)}</li>" for f in d["ferdigheter"])}</ul>
</body></html>
"""


def finn_chrome():
    for c in CHROME_KANDIDATER:
        if Path(c).exists() or shutil.which(c):
            return c
    return None


def main():
    d = les_innhold()
    (ROT / "index.html").write_text(lag_forside(d), encoding="utf-8")
    print("✓ index.html")

    mappe = ROT / "prosjekter"
    mappe.mkdir(exist_ok=True)
    for gammel in mappe.glob("*.html"):
        gammel.unlink()
    ps = d["prosjekter"]
    for i, p in enumerate(ps):
        html = lag_prosjektside(d, p, ps[i - 1], ps[(i + 1) % len(ps)])
        (mappe / f'{p["slug"]}.html').write_text(html, encoding="utf-8")
    print(f"✓ prosjekter/ ({len(ps)} sider)")

    chrome = finn_chrome()
    if not chrome:
        sys.exit("Fant ikke Google Chrome – PDF ble ikke laget.")
    tmp = ROT / ".pdf-kilde.html"
    tmp.write_text(lag_pdf_html(d), encoding="utf-8")
    try:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={ROT / 'portefolje-kort.pdf'}", tmp.as_uri()],
            check=True, capture_output=True,
        )
    finally:
        tmp.unlink(missing_ok=True)
    print("✓ portefolje-kort.pdf")


if __name__ == "__main__":
    main()
