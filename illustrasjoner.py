"""Egne illustrasjoner for porteføljen: personer (deltakere) og papirhatter.

Personene settes sammen av noen få valg, så de ser like ut gjennom hele
porteføljen. Brukes fra innhold.json som f.eks.
  "figur": {"har": "kort", "harfarge": "brun", "hud": 2, "topp": "aksent", "ting": "mobil"}

  har:      kort, lang, knute, hestehale, krøller, skallet
  harfarge: svart, brun, blond, rød, grå   (eller en hex-farge)
  hud:      1–5 (lys til mørk)
  topp:     aksent (prosjektets farge), gra, sand, oliven, rust, bla, hvit (eller hex)
  bukse:    mork (standard), dongeri, sand (eller hex)
  ting:     mobil, nettbrett, laptop, kolbe (eller ingen)
  briller:  true/false     skjegg: true/false     frakk: true/false (hvit frakk)
  hatt:     hex-farge – papirhatt i stedet for hår (f.eks. workshop-roller)
  arm:      vinkel for høyre arm, strukket ut (0 = rett ned, 90 = rett ut); armlengde: standard 58
"""
import math

HUD = ["#f3d2b8", "#e3b48e", "#c98e64", "#9a6440", "#6b4128"]
HARFARGE = {"svart": "#23201f", "brun": "#5a3a26", "blond": "#d9b25c", "rød": "#a8492b", "grå": "#a7a39c"}
TOPP = {
    "aksent": "var(--aksent)", "gra": "#8c939e", "sand": "#d8c7a6", "oliven": "#7c8a4e",
    "rust": "#b8643c", "bla": "#4f6fa3", "hvit": "#f2f2ef",
}
BUKSE = {"mork": "#2c3038", "dongeri": "#46597a", "sand": "#b9a888"}
MORK = "#22262f"


def _farge(verdi, tabell, standard):
    if not verdi:
        return tabell[standard]
    return tabell.get(verdi, verdi)


def _papirhatt(farge, x, y, b):
    """Brettet papirhatt: trekant med brem. (x, y) er midt på bremmen, b er bredden."""
    h = b * 0.62
    return (
        f'<path d="M{x - b/2 + 3} {y} L{x} {y - h} L{x + b/2 - 3} {y} Z" fill="{farge}"/>'
        f'<path d="M{x} {y - h} L{x - b*0.16} {y}" stroke="#000" stroke-opacity=".18" stroke-width="1.4"/>'
        f'<rect x="{x - b/2}" y="{y - 3}" width="{b}" height="9" rx="2" fill="{farge}"/>'
        f'<rect x="{x - b/2}" y="{y - 3}" width="{b}" height="9" rx="2" fill="#000" fill-opacity=".14"/>'
    )


def _figur(f):
    """Delene til en stående person (i personens eget koordinatsystem 120 × 250)."""
    f = f or {}
    hud = HUD[max(1, min(5, int(f.get("hud", 2)))) - 1]
    har = f.get("har", "kort")
    harf = _farge(f.get("harfarge"), HARFARGE, "brun")
    topp = _farge(f.get("topp"), TOPP, "gra")
    bukse = _farge(f.get("bukse"), BUKSE, "mork")
    ting = f.get("ting")
    frakk = f.get("frakk")
    erme = "#ecebe7" if frakk else topp

    d = ['<ellipse cx="60" cy="243" rx="30" ry="4.5" fill="#000" fill-opacity=".09"/>']

    # Hår bak hodet
    if har == "lang" and not f.get("hatt"):
        d.append(f'<path d="M41 42 C40 20 80 20 79 42 L81 80 C72 85 48 85 39 80 Z" fill="{harf}"/>')
    if har == "hestehale" and not f.get("hatt"):
        d.append(f'<path d="M72 28 C92 30 94 58 82 74 C85 56 80 42 70 38 Z" fill="{harf}"/>')

    # Bein og sko
    d.append(f'<rect x="46.5" y="144" width="12.5" height="92" rx="6" fill="{bukse}"/>')
    d.append(f'<rect x="61" y="144" width="12.5" height="92" rx="6" fill="{bukse}"/>')
    d.append(f'<ellipse cx="50" cy="238" rx="10" ry="5" fill="{MORK}"/>')
    d.append(f'<ellipse cx="70" cy="238" rx="10" ry="5" fill="{MORK}"/>')

    # Venstre arm (hengende)
    d.append(f'<rect x="29" y="78" width="11.5" height="64" rx="5.75" fill="{erme}"/>')
    d.append(f'<rect x="29" y="78" width="11.5" height="64" rx="5.75" fill="#000" fill-opacity=".08"/>')
    d.append(f'<circle cx="34.75" cy="144" r="5.6" fill="{hud}"/>')

    # Hals og overkropp
    d.append(f'<rect x="54.5" y="54" width="11" height="18" rx="3.5" fill="{hud}"/>')
    d.append(f'<path d="M40 86 C40 74 46 70 54 69 H66 C74 70 80 74 80 86 L82.5 152 H37.5 Z" fill="{topp}"/>')
    if frakk:
        d.append('<path d="M40 86 C40 74 46 70 54 69 H57 L55 162 H36 Z" fill="#f2f1ed"/>')
        d.append('<path d="M80 86 C80 74 74 70 66 69 H63 L65 162 H84 Z" fill="#e6e4df"/>')

    # Høyre arm: strukket ut i en vinkel, bøyd når personen holder noe foran seg, ellers hengende
    if "arm" in f:
        hx, hy = _hand(f)
        for farge, opasitet in ((erme, 1), ("#000", .08)):
            d.append(f'<path d="M85 84 L{hx:.1f} {hy:.1f}" stroke="{farge}" stroke-opacity="{opasitet}" '
                     'stroke-width="11.5" stroke-linecap="round"/>')
        d.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="5.6" fill="{hud}"/>')
    elif ting in ("mobil", "nettbrett", "kolbe"):
        d.append(f'<path d="M85 84 L89 118 L73 110" fill="none" stroke="{erme}" stroke-width="11.5" '
                 'stroke-linecap="round" stroke-linejoin="round"/>')
        d.append(f'<path d="M85 84 L89 118 L73 110" fill="none" stroke="#000" stroke-opacity=".08" stroke-width="11.5" '
                 'stroke-linecap="round" stroke-linejoin="round"/>')
        if ting == "mobil":
            d.append(f'<rect x="66" y="93" width="10" height="17" rx="2.2" fill="{MORK}"/>')
        elif ting == "nettbrett":
            d.append(f'<rect x="56" y="90" width="24" height="30" rx="3" fill="{MORK}" transform="rotate(-8 68 105)"/>')
            d.append('<rect x="59" y="93" width="18" height="24" rx="1.5" fill="#dfe6ee" transform="rotate(-8 68 105)"/>')
        else:
            d.append('<path d="M68 90 h7 v8 l7 14 a3 3 0 0 1 -3 4 h-15 a3 3 0 0 1 -3 -4 l7 -14 z" fill="#dfe6ee" '
                     f'stroke="{MORK}" stroke-width="1.6" stroke-linejoin="round"/>')
            d.append('<path d="M63.5 107 h17 l2 4.5 a3 3 0 0 1 -3 4 h-15 a3 3 0 0 1 -3 -4 z" fill="var(--aksent)"/>')
        d.append(f'<circle cx="72" cy="109.5" r="5.6" fill="{hud}"/>')
    else:
        d.append(f'<rect x="79.5" y="78" width="11.5" height="64" rx="5.75" fill="{erme}"/>')
        d.append(f'<rect x="79.5" y="78" width="11.5" height="64" rx="5.75" fill="#000" fill-opacity=".08"/>')
        d.append(f'<circle cx="85.25" cy="144" r="5.6" fill="{hud}"/>')
        if ting == "laptop":
            d.append('<rect x="84" y="98" width="9" height="36" rx="2" fill="#c7ccd4"/>')
            d.append('<rect x="84" y="98" width="3" height="36" rx="1.5" fill="#aab1bb"/>')

    # Hode
    d.append(f'<circle cx="60" cy="40" r="17" fill="{hud}"/>')
    if f.get("skjegg"):
        d.append(f'<path d="M44.5 44 C46 60 74 60 75.5 44 C71 52 49 52 44.5 44 Z" fill="{harf}"/>')

    # Hår foran / hatt
    if f.get("hatt"):
        d.append(_papirhatt(f["hatt"], 60, 29, 44))
    elif har in ("kort", "lang", "knute", "hestehale"):
        d.append(f'<path d="M42.6 46 C40 24 50 19 60 19 C71 19 80 25 77.4 46 L75.5 40 C72 33 66 30 60 30 '
                 f'C54 30 48 33 44.5 40 Z" fill="{harf}"/>')
        if har == "knute":
            d.append(f'<circle cx="60" cy="17" r="8" fill="{harf}"/>')
    elif har == "krøller":
        for cx, cy, r in [(45, 34, 7), (51, 25, 7.5), (60, 21.5, 8), (69, 25, 7.5), (75, 34, 7), (43.5, 42, 5), (76.5, 42, 5)]:
            d.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{harf}"/>')

    if f.get("briller"):
        d.append(f'<g fill="none" stroke="{MORK}" stroke-width="1.6"><circle cx="53.5" cy="41" r="4.6"/>'
                 '<circle cx="66.5" cy="41" r="4.6"/><path d="M58.1 41 h3.8"/></g>')

    return "".join(d)


def _hand(f):
    """Håndens posisjon når armen er strukket ut: `arm` er vinkelen fra rett ned (90 = rett ut)."""
    v, lengde = math.radians(f["arm"]), f.get("armlengde", 58)
    return 85 + lengde * math.sin(v), 84 + lengde * math.cos(v)


def person(f=None, tittel=""):
    """En stående person som inline SVG."""
    rolle = f' role="img" aria-label="{tittel}"' if tittel else ' aria-hidden="true"'
    return f'<svg class="person" viewBox="0 -6 120 256"{rolle}>{_figur(f or {})}</svg>'


# Ferdige figurer til testpersoner o.l., så de varierer uten å måtte beskrives hver gang
TESTPERSONER = [
    {"har": "hestehale", "harfarge": "grå", "hud": 1, "topp": "gra", "ting": "mobil"},
    {"har": "hestehale", "harfarge": "rød", "hud": 2, "topp": "aksent", "ting": "mobil"},
    {"har": "kort", "harfarge": "blond", "hud": 3, "topp": "rust", "ting": "mobil", "bukse": "dongeri"},
    {"har": "kort", "harfarge": "svart", "hud": 4, "topp": "sand", "ting": "mobil"},
    {"har": "krøller", "harfarge": "svart", "hud": 5, "topp": "oliven", "ting": "mobil"},
    {"har": "lang", "harfarge": "brun", "hud": 2, "topp": "bla", "ting": "mobil", "briller": True},
    {"har": "knute", "harfarge": "svart", "hud": 3, "topp": "aksent", "ting": "mobil", "bukse": "sand"},
    {"har": "kort", "harfarge": "brun", "hud": 1, "topp": "oliven", "ting": "mobil", "briller": True},
]


def testpersoner(antall, start=0):
    """`antall` ulike figurer fra TESTPERSONER, fra posisjon `start`."""
    return [TESTPERSONER[(start + n) % len(TESTPERSONER)] for n in range(antall)]


# ---------- Scener: før/etter-ruter der en person bruker hånden (f.eks. Charm) ----------
SKALA, PX, PY = .86, 75, 12            # personens plassering i ruten (300 × 240)
SCENEPERSON = {"har": "hestehale", "harfarge": "svart", "hud": 4, "topp": "aksent", "bukse": "dongeri"}
_scener = 0


def _mot(x, y):
    """Arm-vinkel og -lengde som får hånden til punktet (x, y) i ruten."""
    dx, dy = (x - PX) / SKALA - 85, (y - PY) / SKALA - 84
    return {"arm": math.degrees(math.atan2(dx, dy)), "armlengde": math.hypot(dx, dy)}


def _glod(pref, x, y, farge, r=19):
    return (f'<radialGradient id="{pref}"><stop offset="0" style="stop-color:{farge};stop-opacity:.95"/>'
            f'<stop offset=".45" style="stop-color:{farge};stop-opacity:.5"/>'
            f'<stop offset="1" style="stop-color:{farge};stop-opacity:0"/></radialGradient>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{pref})"/>')


def _gnist(x, y, s=5):
    return (f'<path d="M{x} {y - s} Q{x} {y} {x + s} {y} Q{x} {y} {x} {y + s} Q{x} {y} {x - s} {y} '
            f'Q{x} {y} {x} {y - s} Z" fill="var(--aksent)"/>')


def _felt(x, y, b, h, tekst=""):
    t = f'<text class="scene-tekst" x="{x + b / 2}" y="{y + 15}" text-anchor="middle">{tekst}</text>' if tekst else ""
    return f'<rect class="scene-felt" x="{x}" y="{y}" width="{b}" height="{h}" rx="3"/>{t}'


def _rute(hand, foran="", bak="", tittel=""):
    """Én rute: bakgrunn, ting bak personen, personen med hånden i `hand`, ting foran."""
    figur = dict(SCENEPERSON, **_mot(*hand))
    return (f'<svg class="scene-rute" viewBox="0 0 300 240" role="img" aria-label="{tittel}">'
            '<rect class="scene-bg" width="300" height="240" rx="16"/>'
            '<rect class="scene-gulv" y="204" width="300" height="36" rx="16"/>'
            f'{bak}<g transform="translate({PX} {PY}) scale({SKALA})">{_figur(figur)}</g>{foran}</svg>')


def scene(navn):
    """To ruter (før → etter) for en gjenkjenningsmetode i Charm."""
    global _scener
    _scener += 1
    p = f"sc{_scener}"
    if navn == "fri-hand":
        a = _rute((175, 128), _glod(p + "a", 175, 128, "#9aa0aa"), tittel="Hand down, not recognized")
        b = _rute((182, 40), _glod(p + "b", 182, 40, "var(--aksent)") + _gnist(204, 26) + _gnist(198, 60, 4) + _gnist(165, 22, 3.5),
                  tittel="Hand raised, posture recognized")
    elif navn == "form":
        T, R, L = (190, 52), (255, 120), (180, 120)
        pil = (f'<defs><marker id="{p}m" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
               '<path d="M1 1 L8 5 L1 9 Z" fill="var(--aksent)"/></marker></defs>')
        trekant = f'<path class="scene-strek" d="M{T[0]} {T[1]} L{R[0]} {R[1]} L{L[0]} {L[1]} Z"/>'
        a = _rute(T, _glod(p + "a", *T, "var(--aksent)") +
                  f'<text class="scene-tekst" x="{T[0] + 14}" y="{T[1] - 12}">Start position</text>',
                  bak=trekant, tittel="Start position of the shape")
        b = _rute(L, _glod(p + "b", *L, "var(--aksent)") + _gnist(205, 98, 6),
                  bak=pil + trekant + f'<path class="scene-spor" d="M{T[0]} {T[1]} L{R[0]} {R[1]} L{L[0] + 12} {L[1]}" '
                  f'marker-end="url(#{p}m)"/>', tittel="Triangle drawn in the air")
    elif navn == "kollider":
        felt = _felt(182, 28, 74, 50, "Collider 1") + _felt(182, 90, 74, 50, "Collider 2")
        a = _rute((172, 128), _glod(p + "a", 172, 128, "#6f86ff"), bak=felt, tittel="Hand outside the colliders")
        b = _rute((205, 60), _glod(p + "b", 205, 60, "#ff4fc8"), bak=felt, tittel="Hand hits collider 1, glow changes colour")
    else:  # posisjon
        akser = ('<path class="scene-akse" d="M24 228 V24 M18 32 L24 24 L30 32 M24 228 H284 M276 222 L284 228 L276 234"/>'
                 '<text class="scene-tekst" x="32" y="30">Y</text><text class="scene-tekst" x="272" y="216">X</text>')
        felt = akser + _felt(168, 30, 40, 40) + _felt(168, 92, 40, 40) + _felt(216, 92, 40, 40)
        kube = lambda x, y, farge: f'<rect x="{x - 9}" y="{y - 20}" width="18" height="18" rx="2" fill="{farge}"/>'
        a = _rute((188, 112), kube(188, 112, "#3fae5b"), bak=felt, tittel="Hand in one area: green cube")
        b = _rute((188, 50), kube(188, 50, "#e5484d"), bak=felt, tittel="Hand in another area: red cube")
    return f'<div class="scene">{a}{b}</div>'


def _postit(x, y, farge, vri=0):
    """Liten post-it med to «tekstlinjer» og skygge."""
    return (f'<g transform="rotate({vri} {x + 22} {y + 22})">'
            f'<rect x="{x + 2}" y="{y + 4}" width="44" height="44" fill="#000" opacity=".12"/>'
            f'<rect x="{x}" y="{y}" width="44" height="44" fill="{farge}"/>'
            f'<path d="M{x + 8} {y + 16} h26 M{x + 8} {y + 25} h20" stroke="#000" stroke-opacity=".25" stroke-width="3" stroke-linecap="round"/></g>')


def seilbat():
    """Seilbåtøvelsen: grønne lapper i vinden (driver fremover), oransje ved ankeret (holder igjen)."""
    vind = "".join(f'<path d="M{x} {y} q30 -14 60 0 t60 0" fill="none" stroke="var(--aksent)" stroke-opacity=".45" '
                   'stroke-width="4" stroke-linecap="round"/>' for x, y in ((40, 92), (70, 122), (30, 152)))
    return (
        '<svg class="seilbat" viewBox="0 0 600 320" role="img" '
        'aria-label="Sailboat exercise: the wind is what pushes the design forward, the anchor is what holds it back">'
        '<rect width="600" height="320" rx="18" fill="var(--ark)"/>'
        '<path d="M0 206 q37 -14 75 0 t75 0 t75 0 t75 0 t75 0 t75 0 t75 0 t75 0 V302 a18 18 0 0 1 -18 18 H18 a18 18 0 0 1 -18 -18 Z" '
        'fill="var(--aksent)" fill-opacity=".18"/>'
        '<path d="M0 236 q37 -10 75 0 t75 0 t75 0 t75 0 t75 0 t75 0 t75 0 t75 0 V302 a18 18 0 0 1 -18 18 H18 a18 18 0 0 1 -18 -18 Z" '
        'fill="var(--aksent)" fill-opacity=".18"/>'
        + vind +
        # båt: mast, seil og skrog
        '<path d="M352 48 V196" stroke="#2c3038" stroke-width="5" stroke-linecap="round"/>'
        '<path d="M357 56 L357 186 L440 186 Z" fill="#fff" stroke="#2c3038" stroke-width="3" stroke-linejoin="round"/>'
        '<path d="M347 72 L347 186 L288 186 Z" fill="#f1f3f8" stroke="#2c3038" stroke-width="3" stroke-linejoin="round"/>'
        '<path d="M262 196 H458 L430 236 H292 Z" fill="var(--aksent)"/>'
        '<path d="M262 196 H458 L452 206 H268 Z" fill="#000" fill-opacity=".15"/>'
        # anker med kjetting
        '<path d="M320 236 V286" stroke="#2c3038" stroke-width="3" stroke-dasharray="5 4"/>'
        '<path d="M320 286 V306 M306 298 q14 16 28 0 M314 290 h12" stroke="#2c3038" stroke-width="4" '
        'stroke-linecap="round" fill="none"/>'
        # lappene
        + _postit(52, 34, "#c5ec7f", -6) + _postit(150, 46, "#c5ec7f", 5) + _postit(96, 168, "#c5ec7f", -3)
        + _postit(230, 258, "#ffa35a", 4) + _postit(370, 262, "#ffa35a", -5) +
        '<text class="seilbat-tekst" x="200" y="30">Wind – what pushes us forward</text>'
        '<text class="seilbat-tekst" x="430" y="296">Anchor – what</text>'
        '<text class="seilbat-tekst" x="430" y="313">holds us back</text>'
        '</svg>'
    )