#!/usr/bin/env python3
"""Bygger index.html (nettside) og portefolje-kort.pdf fra innhold.json.

Bruk:  python3 bygg.py
PDF-en lages med Google Chrome i headless-modus.
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


def lenker(k):
    deler = []
    if k.get("epost"):
        deler.append(f'<a href="mailto:{e(k["epost"])}">{e(k["epost"])}</a>')
    if k.get("linkedin"):
        deler.append(f'<a href="{e(k["linkedin"])}">LinkedIn</a>')
    if k.get("github"):
        deler.append(f'<a href="{e(k["github"])}">GitHub</a>')
    return deler


def prosjektkort(p):
    bilde = f'<img src="{e(p["bilde"])}" alt="" loading="lazy">' if p.get("bilde") else ""
    stikkord = "".join(f"<li>{e(s)}</li>" for s in p.get("stikkord", []))
    resultat = f'<p class="resultat">{e(p["resultat"])}</p>' if p.get("resultat") else ""
    lenke = f'<a class="mer" href="{e(p["lenke"])}">Se prosjektet →</a>' if p.get("lenke") else ""
    return f"""
      <article class="kort">
        {bilde}
        <div class="meta">{e(p.get("aar", ""))} · {e(p.get("rolle", ""))}</div>
        <h3>{e(p["tittel"])}</h3>
        <p>{e(p.get("beskrivelse", ""))}</p>
        {resultat}
        <ul class="stikkord">{stikkord}</ul>
        {lenke}
      </article>"""


def tidslinje(rader, tittel_felt, under_felt):
    return "".join(
        f"""
      <li>
        <span class="periode">{e(r["periode"])}</span>
        <div><strong>{e(r[tittel_felt])}</strong> — {e(r[under_felt])}
        {f'<p>{e(r["beskrivelse"])}</p>' if r.get("beskrivelse") else ""}</div>
      </li>"""
        for r in rader
    )


def lag_nettside(d):
    k = d["kontakt"]
    return f"""<!doctype html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(d["navn"])} – Portefølje</title>
<meta name="description" content="{e(d["ingress"])}">
<link rel="stylesheet" href="stil.css">
</head>
<body>
<header class="topp">
  <div class="bredde">
    <p class="overtittel">Portefølje</p>
    <h1>{e(d["navn"])}</h1>
    <p class="tittel">{e(d["tittel"])}</p>
    <p class="ingress">{e(d["ingress"])}</p>
    <nav class="kontakt">{" · ".join(lenker(k))}</nav>
  </div>
</header>
<main class="bredde">
  <section id="prosjekter">
    <h2>Utvalgte prosjekter</h2>
    <div class="rutenett">{"".join(prosjektkort(p) for p in d["prosjekter"])}
    </div>
  </section>
  <section id="ferdigheter">
    <h2>Ferdigheter</h2>
    <ul class="stikkord stor">{"".join(f"<li>{e(f)}</li>" for f in d["ferdigheter"])}</ul>
  </section>
  <section id="erfaring">
    <h2>Erfaring</h2>
    <ul class="tidslinje">{tidslinje(d["erfaring"], "stilling", "arbeidsgiver")}</ul>
  </section>
  <section id="utdanning">
    <h2>Utdanning</h2>
    <ul class="tidslinje">{tidslinje(d["utdanning"], "grad", "sted")}</ul>
  </section>
</main>
<footer class="bredde">
  <p>{e(k.get("sted", ""))} · <a href="mailto:{e(k.get("epost", ""))}">Ta kontakt</a></p>
</footer>
</body>
</html>
"""


def lag_pdf_html(d):
    """Kortversjon: én A4-side med det viktigste."""
    k = d["kontakt"]
    kontaktlinje = " · ".join(
        x for x in [k.get("epost"), k.get("sted"), k.get("linkedin"), k.get("github")] if x
    )
    prosjekter = "".join(
        f"""
      <div class="p">
        <div class="ph"><strong>{e(p["tittel"])}</strong><span>{e(p.get("aar", ""))} · {e(p.get("rolle", ""))}</span></div>
        <p>{e(p.get("beskrivelse", ""))}</p>
        {f'<p class="res">→ {e(p["resultat"])}</p>' if p.get("resultat") else ""}
      </div>"""
        for p in d["prosjekter"]
    )
    erfaring = "".join(
        f'<li><span>{e(r["periode"])}</span>{e(r["stilling"])}, {e(r["arbeidsgiver"])}</li>'
        for r in d["erfaring"]
    )
    utdanning = "".join(
        f'<li><span>{e(r["periode"])}</span>{e(r["grad"])}, {e(r["sted"])}</li>'
        for r in d["utdanning"]
    )
    return f"""<!doctype html>
<html lang="no"><head><meta charset="utf-8">
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
  .p {{ margin-bottom: 8pt; break-inside: avoid; }}
  .ph {{ display: flex; justify-content: space-between; gap: 8pt; }}
  .ph span {{ color: #5b6573; font-size: 8.5pt; white-space: nowrap; }}
  .p p {{ margin: 2pt 0 0; }}
  .res {{ color: #2a5bd7; font-weight: 600; }}
  .kol {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 18pt; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  .liste li {{ margin-bottom: 3pt; }}
  .liste span {{ display: inline-block; width: 78pt; color: #5b6573; font-size: 8.5pt; }}
  .ferd {{ display: flex; flex-wrap: wrap; gap: 4pt; }}
  .ferd li {{ background: #eef2fb; color: #1e3f99; padding: 1.5pt 6pt; border-radius: 8pt; font-size: 8.5pt; }}
</style></head>
<body>
  <h1>{e(d["navn"])}</h1>
  <div class="tittel">{e(d["tittel"])}</div>
  <div class="kontakt">{e(kontaktlinje)}</div>
  <p class="ingress">{e(d["ingress"])}</p>
  <hr>
  <h2>Utvalgte prosjekter</h2>{prosjekter}
  <div class="kol">
    <div><h2>Erfaring</h2><ul class="liste">{erfaring}</ul></div>
    <div><h2>Utdanning</h2><ul class="liste">{utdanning}</ul>
      <h2>Ferdigheter</h2><ul class="ferd">{"".join(f"<li>{e(f)}</li>" for f in d["ferdigheter"])}</ul></div>
  </div>
</body></html>
"""


def finn_chrome():
    for c in CHROME_KANDIDATER:
        if Path(c).exists() or shutil.which(c):
            return c
    return None


def main():
    d = les_innhold()
    (ROT / "index.html").write_text(lag_nettside(d), encoding="utf-8")
    print("✓ index.html")

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
