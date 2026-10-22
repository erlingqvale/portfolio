#!/usr/bin/env python3
"""Bygger nettsiden og portefolje-kort.pdf fra innhold.json.

Bruk:  python3 bygg.py
Lager index.html (one-pager med alle prosjekter) og PDF-en
(via Google Chrome i headless-modus).
"""
import json
import shutil
import subprocess
import sys
from datetime import date
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


LINKEDIN_LOGO = (
    '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">'
    '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05'
    'c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13z'
    'M7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45'
    'c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>'
)


def lenker(k):
    deler = []
    if k.get("linkedin"):
        deler.append(f'<a href="{e(k["linkedin"])}">{LINKEDIN_LOGO}LinkedIn</a>')
    if k.get("epost"):
        deler.append(f'<a href="mailto:{e(k["epost"])}">{e(k["epost"])}</a>')
    if k.get("telefon"):
        tlf = k["telefon"].replace(" ", "")
        deler.append(f'<a href="tel:{e(tlf)}">{e(k["telefon"])}</a>')
    if k.get("github"):
        deler.append(f'<a href="{e(k["github"])}">GitHub</a>')
    return deler


def stikkord(liste, klasse="stikkord"):
    return f'<ul class="{klasse}">{"".join(f"<li>{e(s)}</li>" for s in liste)}</ul>'


def side(tittel, beskrivelse, kropp):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(tittel)}</title>
<meta name="description" content="{e(beskrivelse)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="stil.css">
</head>
<body>
{kropp}
</body>
</html>
"""


def stegbilde(r):
    """Valgfritt bilde til et løsningskort eller prosessteg."""
    return f'<img src="{e(r["bilde"])}" alt="{e(r["tittel"])}" loading="lazy">' if r.get("bilde") else ""


def blokker(rader, klasse):
    return "".join(
        f'<div class="{klasse}">{stegbilde(r)}<h4>{e(r["tittel"])}</h4><p>{e(r["tekst"])}</p></div>'
        for r in rader
    )


def palett(p):
    """Prosjektets egen fargepalett som CSS-variabler (tom hvis ingen er satt)."""
    f = p.get("farger")
    return f' style="--aksent: {e(f["aksent"])}; --flate: {e(f["flate"])}"' if f else ""


def prosjektseksjon(p):
    bilde = f'<img class="hovedbilde" src="{e(p["bilde"])}" alt="{e(p["tittel"])}" loading="lazy">' if p.get("bilde") else ""
    losning = (
        f'<h3>The solution</h3><div class="rutenett">{blokker(p["losning"], "kort")}</div>'
        if p.get("losning") else ""
    )
    prosess = (
        '<h3>The process</h3><ol class="prosess">'
        + "".join(f'<li><h4>{e(s["tittel"])}</h4><p>{e(s["tekst"])}</p>{stegbilde(s)}</li>' for s in p["prosess"])
        + "</ol>"
        if p.get("prosess") else ""
    )
    lenke = f'<p><a class="mer" href="{e(p["lenke"])}">View project →</a></p>' if p.get("lenke") else ""
    oppsummering = (
        '<aside class="oppsummering"><p>Summary</p><ul>'
        + "".join(f"<li>{e(x)}</li>" for x in p["oppsummering"])
        + "</ul></aside>"
        if p.get("oppsummering") else ""
    )
    return f"""
  <section class="prosjekt ark" id="{e(p["slug"])}"{palett(p)}>
    <h2 class="stortord">{e(p["tittel"])}</h2>
    {oppsummering}
    {stikkord(p.get("stikkord", []))}
    {bilde}
    <h3>The challenge</h3>
    <p class="tekst">{e(p.get("utfordring", ""))}</p>{lenke}
    {losning}
    {prosess}
  </section>"""


# Markerer prosjektet som vises i navigasjonen mens man scroller.
SCROLLSPY = """<script>
const lenker = document.querySelectorAll('.toppmeny a[href^="#"]');
const seksjoner = [...lenker].map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
let forrige = null;
function oppdater() {
  const linje = window.innerHeight * 0.3;
  let aktiv = seksjoner[0];
  for (const s of seksjoner) if (s.getBoundingClientRect().top <= linje) aktiv = s;
  if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 2) aktiv = seksjoner[seksjoner.length - 1];
  if (aktiv === forrige) return;
  forrige = aktiv;
  lenker.forEach(a => a.classList.toggle('aktiv', a.getAttribute('href') === '#' + aktiv.id));
}
addEventListener('scroll', oppdater, { passive: true });
addEventListener('resize', oppdater);
addEventListener('load', oppdater);
oppdater();

// Hamburgermeny på mobil
const meny = document.querySelector('.toppmeny');
const knapp = document.querySelector('.menyknapp');
function settMeny(åpen) {
  meny.classList.toggle('apen', åpen);
  knapp.setAttribute('aria-expanded', åpen);
  knapp.setAttribute('aria-label', åpen ? 'Close menu' : 'Menu');
}
knapp.addEventListener('click', () => settMeny(!meny.classList.contains('apen')));
lenker.forEach(a => a.addEventListener('click', () => settMeny(false)));
addEventListener('keydown', e => { if (e.key === 'Escape') settMeny(false); });

// Menyen er gjennomsiktig helt øverst og får bakgrunn når man har scrollet
function rullet() { meny.classList.toggle('rullet', scrollY > 8); }
addEventListener('scroll', rullet, { passive: true });
rullet();
</script>"""


def lag_forside(d):
    meny = "".join(f'<a href="#{e(p["slug"])}"{palett(p)}>{e(p["tittel"])}</a>' for p in d["prosjekter"])
    kropp = f"""<nav class="toppmeny">
  <div class="bredde">
    <a class="navn" href="#top">EQ Portfolio</a>
    <button class="menyknapp" type="button" aria-label="Menu" aria-expanded="false" aria-controls="menyliste">
      <span></span><span></span><span></span>
    </button>
    <div class="menyliste" id="menyliste">{meny}<a class="knapp" href="#contact">Contact</a></div>
  </div>
</nav>
<header class="topp" id="top">
  <img class="forsidebilde" src="bilder/generelt/stonehenge-1600.jpg"
    srcset="bilder/generelt/stonehenge-900.jpg 900w, bilder/generelt/stonehenge-1600.jpg 1600w, bilder/generelt/stonehenge-2400.jpg 2400w"
    sizes="(orientation: portrait) 150vh, 100vw" alt="" fetchpriority="high">
  <div class="bredde">
    <p class="hei">Hi, I'm {e(d["navn"])}</p>
    <h1>{e(d["tittel"])}</h1>
  </div>
  <a class="nedpil" href="#{e(d["prosjekter"][0]["slug"])}" aria-label="Scroll to projects">
    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v16M5 13l7 7 7-7"/></svg>
  </a>
</header>
<main class="bredde">{"".join(prosjektseksjon(p) for p in d["prosjekter"])}
  <section class="kontaktseksjon" id="contact">
    <div class="kontaktinnhold">
      <h2>Let's connect</h2>
      <ul class="kontaktknapper">{"".join(f"<li>{l}</li>" for l in lenker(d["kontakt"]))}</ul>
      <h3>Skills &amp; tools</h3>
      {stikkord(d["ferdigheter"], "stikkord stor")}
    </div>
    <footer class="bunn">
      <span>© {date.today().year} {e(d["navn"])}</span>
      <a href="#top">Back to top
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20V4M5 11l7-7 7 7"/></svg>
      </a>
    </footer>
  </section>
</main>
{SCROLLSPY}"""
    return side(f'{d["navn"]} – Portfolio', d["ingress"], kropp)


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
