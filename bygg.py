#!/usr/bin/env python3
"""Bygger nettsiden og portefolje-kort.pdf fra innhold.json.

Bruk:  python3 bygg.py
Lager index.html (one-pager med alle prosjekter) og PDF-en
(via Google Chrome i headless-modus).
"""
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from html import escape as e
from pathlib import Path
from urllib.parse import quote

from annotering import annotert
from illustrasjoner import person, testpersoner

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


def ikon(navn, str_=18):
    """Lucide-ikon (ikoner/<navn>.svg, ISC-lisens) bakt inn i siden."""
    svg = (ROT / "ikoner" / f"{navn}.svg").read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S)
    # Fjern class/width/height bare på selve <svg>-taggen (rect o.l. trenger sine)
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s+(class|width|height)="[^"]*"', "", m.group()), svg, count=1)
    svg = re.sub(r"\s+", " ", svg).replace("> <", "><").strip()
    return svg.replace("<svg", f'<svg width="{str_}" height="{str_}" aria-hidden="true"', 1)


def lenker(k):
    deler = []
    if k.get("linkedin"):
        deler.append(f'<a href="{e(k["linkedin"])}" target="_blank" rel="noopener">{ikon("linkedin")}LinkedIn</a>')
    # E-post og telefon kopieres ved klikk (se KOPIER); mailto/tel er reserve uten JavaScript
    if k.get("epost"):
        deler.append(f'<a href="mailto:{e(k["epost"])}" data-kopier="{e(k["epost"])}">{e(k["epost"])}</a>')
    if k.get("telefon"):
        tlf = k["telefon"].replace(" ", "")
        deler.append(f'<a href="tel:{e(tlf)}" data-kopier="{e(k["telefon"])}">{e(k["telefon"])}</a>')
    if k.get("github"):
        deler.append(f'<a href="{e(k["github"])}">GitHub</a>')
    return deler


def ekstralenker(rader):
    """Lenker nederst på siden, f.eks. bachelor- og masteroppgave."""
    if not rader:
        return ""
    return '<h3>Further reading</h3><ul class="ekstralenker">' + "".join(
        f'<li><a href="{e(r["lenke"])}" target="_blank" rel="noopener">{e(r["tittel"])}'
        + (f'<span>{e(r["tekst"])}</span>' if r.get("tekst") else "")
        + '</a></li>'
        for r in rader
    ) + "</ul>"


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


def bildefil(sti, alt):
    return f'<img src="{e(quote(sti))}" alt="{e(alt)}" loading="lazy">'


def stegbilde(r):
    """Valgfritt bilde til et løsningskort eller prosessteg."""
    return bildefil(r["bilde"], r["tittel"]) if r.get("bilde") else ""


def deltakere(liste):
    """Illustrerte deltakere, ev. med rolle og sitater i snakkebobler."""
    if not liste:
        return ""
    sitater = any(d.get("sitater") for d in liste)
    rader = []
    for d in liste:
        bobler = "".join(f'<blockquote class="boble">“{e(x)}”</blockquote>' for x in d.get("sitater", []))
        rolle = f'<strong class="rolle">{e(d["rolle"])}</strong>' if d.get("rolle") else ""
        navn = f'<span class="navn">{e(d["navn"])}</span>' if d.get("navn") else ""
        rader.append(f'<li>{f"<div class=bobler>{bobler}</div>" if bobler else ""}{rolle}'
                     f'{person(d.get("figur"))}{navn}</li>')
    return f'<ul class="deltakere{" med-sitater" if sitater else ""}">{"".join(rader)}</ul>'


def roller(liste):
    """Roller med hver sin papirhatt (f.eks. optimist/pessimist/opportunist)."""
    return '<ul class="roller">' + "".join(
        f'<li>{person(dict(r.get("figur", {}), hatt=r["farge"]))}'
        f'<div><strong>{e(r["tittel"])}</strong><p>{e(r["tekst"])}</p></div></li>'
        for r in liste
    ) + "</ul>"


def delbilder(bilder, alt):
    """Bilder i en del: enten bare filstier, eller {"fil", "tittel", "tekst"} med bildetekst under."""
    if all(isinstance(b, str) for b in bilder):
        return f'<div class="delbilder">{"".join(bildefil(b, alt) for b in bilder)}</div>'
    return '<div class="delbilder forklart">' + "".join(
        f'<figure>{bildefil(b["fil"], b.get("tittel", alt))}<figcaption>'
        + (f'<strong>{e(b["tittel"])}</strong>' if b.get("tittel") else "")
        + f'{e(b.get("tekst", ""))}</figcaption></figure>'
        for b in bilder
    ) + "</div>"


def deler(liste):
    """Et prosessteg delt opp i deler (Part 1, Part 2 …) med bilder eller roller."""
    if not liste:
        return ""
    return '<ol class="deler">' + "".join(
        f'<li><span class="delnr">Part {i}</span><h5>{e(x["tittel"])}</h5><p>{e(x["tekst"])}</p>'
        + (roller(x["roller"]) if x.get("roller") else "")
        + (delbilder(x["bilder"], x["tittel"]) if x.get("bilder") else "")
        + "</li>"
        for i, x in enumerate(liste, 1)
    ) + "</ol>"


def punkter(s):
    """Valgfri punktliste og lenke i et prosessteg (f.eks. hva testene endret)."""
    liste = f'<ul class="punkter">{"".join(f"<li>{e(x)}</li>" for x in s["punkter"])}</ul>' if s.get("punkter") else ""
    lenke = f'<p><a class="mer" href="{e(s["lenke"]["href"])}">{e(s["lenke"]["tekst"])}</a></p>' if s.get("lenke") else ""
    return liste + lenke


def funn(s):
    """Funn fra en brukertest (tommel opp/ned) og antall testpersoner som figurer."""
    if not s.get("funn"):
        return ""
    kort = "".join(
        f'<li class="{"pluss" if f["type"] == "pluss" else "minus"}">'
        f'{ikon("thumbs-up" if f["type"] == "pluss" else "thumbs-down", 30)}<span>{e(f["tekst"])}</span></li>'
        for f in s["funn"]
    )
    antall = s.get("testpersoner", 0)
    folk = ""
    if antall:
        figurer = "".join(person(f) for f in testpersoner(antall, s.get("figurstart", 0)))
        folk = f'<div class="testpersoner"><div>{figurer}</div><span>{antall} participants</span></div>'
    return f'<ul class="funnliste">{kort}</ul>{folk}'


def prosessteg(s):
    return (f'<li><h4>{e(s["tittel"])}</h4><p>{e(s["tekst"])}</p>{funn(s)}{punkter(s)}'
            f'{deltakere(s.get("deltakere"))}{deler(s.get("deler"))}{annotert(s.get("annotert"))}{stegbilde(s)}</li>')


def blokker(rader, klasse):
    return "".join(
        f'<div class="{klasse}">{stegbilde(r)}<h4>{e(r["tittel"])}</h4><p>{e(r["tekst"])}</p></div>'
        for r in rader
    )


def video(p):
    """Valgfri video av løsningen: lokal fil (bilder/<prosjekt>/x.mp4) eller YouTube-/Vimeo-lenke."""
    v = p.get("video")
    if not v:
        return ""
    if "youtube.com/watch?v=" in v or "youtu.be/" in v:
        id_ = v.split("v=")[-1].split("&")[0] if "v=" in v else v.rsplit("/", 1)[-1].split("?")[0]
        src = f"https://www.youtube-nocookie.com/embed/{id_}"
    elif "vimeo.com/" in v:
        src = f"https://player.vimeo.com/video/{v.rstrip('/').rsplit('/', 1)[-1]}"
    else:
        plakat = Path(v).with_suffix(".jpg")
        # Uten plakatbilde lastes metadata, så nettleseren viser første bilde i videoen
        plakat = f' poster="{e(str(plakat))}" preload="none"' if (ROT / plakat).exists() else ' preload="metadata"'
        return f'<video class="video" src="{e(v)}"{plakat} controls playsinline></video>'
    return (f'<div class="video"><iframe src="{e(src)}" title="{e(p["tittel"])} – video" '
            'allow="fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>')


def tidslinje(p):
    """Prosessen i korte trekk: ikon i sirkel, pil mellom stegene."""
    steg = p.get("tidslinje")
    if not steg:
        return ""
    return '<h3>Design process</h3><ol class="tidslinje">' + "".join(
        f'<li><span class="sirkel">{ikon(s["ikon"], 28)}</span><span class="steg">{e(s["tittel"])}</span>'
        + (f'<span class="pil">{ikon("arrow-right", 22)}</span>' if i < len(steg) - 1 else "")
        + "</li>"
        for i, s in enumerate(steg)
    ) + "</ol>"


def palett(p):
    """Prosjektets egen fargepalett som CSS-variabler (tom hvis ingen er satt)."""
    f = p.get("farger")
    return f' style="--aksent: {e(f["aksent"])}; --flate: {e(f["flate"])}"' if f else ""


def prosjektseksjon(p):
    bilde = f'<img class="hovedbilde" src="{e(p["bilde"])}" alt="{e(p["tittel"])}" loading="lazy">' if p.get("bilde") else ""
    kort = f'<div class="rutenett">{blokker(p["losning"], "kort")}</div>' if p.get("losning") else ""
    losning = f'<h3 id="{e(p["slug"])}-losning">The solution</h3>{kort}' if kort else ""
    prosess = (
        '<h3>The process</h3><ol class="prosess">'
        + "".join(prosessteg(s) for s in p["prosess"])
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
    {video(p) or bilde}
    <h3>The challenge</h3>
    <p class="tekst">{e(p.get("utfordring", ""))}</p>{lenke}
    {losning}
    {tidslinje(p)}
    {prosess}
  </section>"""


# Kopierer e-post/telefon ved klikk og viser en kort bekreftelse.
KOPIER = """<script>
const status = document.querySelector('.kopistatus');
let tidtaker;
document.querySelectorAll('[data-kopier]').forEach(a => a.addEventListener('click', async ev => {
  if (!navigator.clipboard) return;
  ev.preventDefault();
  try {
    await navigator.clipboard.writeText(a.dataset.kopier);
    status.textContent = 'Copied ' + a.dataset.kopier;
    status.classList.add('vis');
    clearTimeout(tidtaker);
    tidtaker = setTimeout(() => status.classList.remove('vis'), 2000);
  } catch { location.href = a.href; }
}));
</script>"""


# Bare én video spiller om gangen: starter man en, pauses de andre.
EN_VIDEO = """<script>
document.addEventListener('play', ev => {
  document.querySelectorAll('video').forEach(v => { if (v !== ev.target) v.pause(); });
}, true);
</script>"""


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
    {ikon("arrow-down", 28)}
  </a>
</header>
<main class="bredde">{"".join(prosjektseksjon(p) for p in d["prosjekter"])}
  <section class="kontaktseksjon" id="contact">
    <div class="kontaktinnhold">
      <h2>Let's connect</h2>
      <ul class="kontaktknapper">{"".join(f"<li>{l}</li>" for l in lenker(d["kontakt"]))}</ul>
      <h3>Skills &amp; tools</h3>
      {stikkord(d["ferdigheter"], "stikkord stor")}
      {ekstralenker(d.get("lenker", []))}
    </div>
    <footer class="bunn">
      <span>© {date.today().year} {e(d["navn"])}</span>
      <a href="#top">Back to top
        {ikon("arrow-up")}
      </a>
    </footer>
  </section>
</main>
<p class="kopistatus" role="status" aria-live="polite"></p>
{SCROLLSPY}{KOPIER}{EN_VIDEO}"""
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
