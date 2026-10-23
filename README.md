# Portefølje – Erling Qvale

Personlig portefølje som nettside (GitHub Pages) og kortversjon i PDF.

## Slik oppdaterer du

1. Rediger innholdet i `innhold.json` (prosjektbilder legges i `bilder/<prosjekt>/`, f.eks. `"bilde": "bilder/fuse/navn.png"`; bilder som ikke hører til et prosjekt – profilbilde, logo, bakgrunner o.l. – legges i `bilder/generelt/`). Video av løsningen settes i `"video"` – enten en lokal fil (`bilder/fuse/demo.mp4`) eller en YouTube-/Vimeo-lenke.
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
