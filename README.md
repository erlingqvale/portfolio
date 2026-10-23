# Portefølje – Erling Qvale

Personlig portefølje som nettside (GitHub Pages) og kortversjon i PDF.

## Slik oppdaterer du

1. Rediger innholdet i `innhold.json` (prosjektbilder legges i `bilder/<prosjekt>/`, f.eks. `"bilde": "bilder/01-fuse/navn.png"`; bilder som ikke hører til et prosjekt – profilbilde, logo, bakgrunner o.l. – legges i `bilder/generelt/`). Video av løsningen settes i `"video"` – enten en lokal fil (`bilder/01-fuse/demo.mp4`) eller en YouTube-/Vimeo-lenke.
   **Navn på filer:** prosjektmappene er nummerert i samme rekkefølge som på siden (`01-fuse`, `02-charm` …), og filene sorteres slik de står på siden: `<seksjon>-<steg>-<detalj>`, der seksjon er `1` video, `2` løsning og `3` prosess. Eksempler: `1-video.mp4`, `2-losning-1-compare.svg`, `3-prosess-04-prototype1-1-hoved.svg`.
2. Kjør `python3 bygg.py` – lager `index.html` (one-pager med alle prosjekter og navigasjon som følger scrollingen) og `portefolje-kort.pdf`.
3. Commit og push – nettsiden oppdateres automatisk.

| Fil | Hva |
|---|---|
| `innhold.json` | All tekst – eneste fil du trenger å redigere |
| `stil.css` | Utseende på nettsiden |
| `illustrasjoner.py` | Egne personfigurer (deltakere) og papirhatter – se toppen av filen for valgene i `"figur"` |
| `annotering.py` | Annoterte prototyper (merkelapper, klammer og piler rundt skissene) – se toppen av filen for `"annotert"` |
| `ikoner/` | Ikoner fra [Lucide](https://lucide.dev) (gratis, ISC-lisens). Nye ikoner: last ned `<navn>.svg` fra lucide.dev hit og bruk navnet, f.eks. `"ikon": "user"` i `"tidslinje"` |
| `bygg.py` | Genererer nettside og PDF |
| `portefolje-kort.pdf` | Kortversjon, kun lokalt (ikke i Git) |
