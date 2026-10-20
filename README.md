# Portefølje – Erling Qvale

Personlig portefølje som nettside (GitHub Pages) og kortversjon i PDF.

## Slik oppdaterer du

1. Rediger innholdet i `innhold.json` (prosjektbilder legges i `bilder/<prosjekt>/`, f.eks. `"bilde": "bilder/fuse/navn.png"`; bilder som ikke hører til et prosjekt – profilbilde, logo, bakgrunner o.l. – legges i `bilder/generelt/`).
2. Kjør `python3 bygg.py` – lager `index.html` (one-pager med alle prosjekter og navigasjon som følger scrollingen) og `portefolje-kort.pdf`.
3. Commit og push – nettsiden oppdateres automatisk.

| Fil | Hva |
|---|---|
| `innhold.json` | All tekst – eneste fil du trenger å redigere |
| `stil.css` | Utseende på nettsiden |
| `bygg.py` | Genererer nettside og PDF |
| `portefolje-kort.pdf` | Kortversjon, kun lokalt (ikke i Git) |
