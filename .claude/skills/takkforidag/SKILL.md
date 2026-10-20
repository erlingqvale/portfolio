---
name: takkforidag
description: Avslutt dagen i porteføljen – bygg på nytt, commit og push alt til GitHub, bekreft at alt ligger oppe, oppsummer dagen, og lukk så terminalen og VS Code. Brukes når brukeren skriver /takkforidag eller sier «takk for i dag».
---

# Takk for i dag

Avslutt arbeidsøkten trygt. Ingenting skal lukkes før det er bekreftet at alt ligger på GitHub.

Kjør alle kommandoer fra prosjektmappen (rotmappen til repoet).

## 1. Bygg på nytt

```bash
python3 bygg.py
```

Stopp og si fra hvis byggingen feiler – ikke commit en ødelagt side.

## 2. Commit og push

```bash
git status --short
```

Hvis det finnes endringer:
- Se på hva som er endret (`git status`, `git diff --stat`), og skriv en kort, beskrivende commit-melding på engelsk om hva som faktisk ble gjort, for eksempel «Add FUSE images and update summaries».
- `git add -A && git commit -m "<melding>"` (med commit-attribusjon slik økten ellers krever).

Push deretter (også hvis det ikke var nye endringer, i tilfelle eldre commits ikke er pushet):

```bash
GIT_TERMINAL_PROMPT=0 git push
```

## 3. Bekreft at alt er oppe

```bash
git fetch -q origin
git status --short          # skal være tom
git rev-parse HEAD          # skal være lik ↓
git rev-parse @{u}
```

Alt er trygt først når arbeidsmappen er ren **og** `HEAD` er lik `@{u}`.

**Hvis noe feiler** (push avvist, ingen tilgang, ulik HEAD, ucommittede filer): forklar hva som er galt og hvordan det løses, og **avslutt uten å lukke noe**. Brukeren skal aldri miste arbeid.

## 4. Oppsummer dagen

Kort på norsk, før noe lukkes:
- Hva som ble lagret i dag (`git log --since=midnight --oneline`).
- Hva som gjenstår, hvis noe er nevnt i økten (f.eks. bilder som mangler).
- En hyggelig avslutning, f.eks. «Takk for i dag! 👋».

## 5. Lukk terminalen og VS Code

Først når steg 3 er bekreftet. Dette avslutter også denne Claude-økten, så det må være siste handling.

```bash
# Terminal.app (hvis økten kjører der)
[ "$TERM_PROGRAM" = "Apple_Terminal" ] && (sleep 2; osascript -e 'quit app "Terminal"') &
# VS Code – lukker også den innebygde terminalen
(sleep 2; osascript -e 'quit app "Visual Studio Code"') &
```

`sleep 2` gir oppsummeringen tid til å vises før appene lukkes. Har VS Code ulagrede filer, spør VS Code selv om de skal lagres – det er ønsket oppførsel.
