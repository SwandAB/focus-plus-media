# Renderingskö för 24-timmarspasset i Higgsfield

Totalt **573 genereringar**: 155 startbilder + 155 videor + 251 karusellomslag + 12 texturer.
På 24 timmar är det i snitt en generering var 2.5 minut. Higgsfield kör flera
genereringar samtidigt, så starta nästa medan föregående renderar.

## Ordning

1. **Pass 1 · Reels januari–mars** (Q1 testar formaten och är viktigast). För varje Reel: steg 1
   startbild, välj den bästa, sedan steg 2 video med den som Start frame.
2. **Pass 2 · Reels april–december.**
3. **Pass 3 · Karusellomslag**, månad för månad.
4. **Pass 4 · Månadens textur** (12 st).

Om tiden tar slut: karusellerna fungerar som ren text på ivory, sage eller rose, precis som i
november–december 2026. Reels kan inte ersättas, så prioritera pass 1 och 2.

## Arbetssätt som sparar tid

- Ha månadsfilen öppen bredvid Higgsfield. Varje prompt ligger i en kodruta med kopieringsknapp.
- Gör alla startbilder för en vecka först, sedan alla videor för samma vecka. Då byter du modell
  mer sällan.
- Spara med filnamnet som står vid varje steg, till exempel `2027-01-04-R-A.mp4`. Lägg allt i en
  mapp per månad. Då kan Claude ladda upp och schemalägga i Postiz efteråt.
- Blir en video fel (konstig hand, flimmer, text i bild): kör om samma prompt en gång. Blir den
  fel igen, hoppa över och markera id:t, så skriver Claude om prompten.
- Bocka av i `data/glowup-2027.csv` (kolumnen `klar`) eller bara i mappen.

## Per månad

| Månad | Startbilder | Videor | Karusellomslag | Textur | Varav Soul-avatar |
|---|---|---|---|---|---|
| [januari](manad/2027-01.md) | 13 | 13 | 18 | 1 | 6 |
| [februari](manad/2027-02.md) | 12 | 12 | 16 | 1 | 5 |
| [mars](manad/2027-03.md) | 14 | 14 | 21 | 1 | 5 |
| [april](manad/2027-04.md) | 12 | 12 | 22 | 1 | 6 |
| [maj](manad/2027-05.md) | 14 | 14 | 22 | 1 | 5 |
| [juni](manad/2027-06.md) | 13 | 13 | 21 | 1 | 4 |
| [juli](manad/2027-07.md) | 13 | 13 | 22 | 1 | 6 |
| [augusti](manad/2027-08.md) | 13 | 13 | 23 | 1 | 7 |
| [september](manad/2027-09.md) | 13 | 13 | 21 | 1 | 7 |
| [oktober](manad/2027-10.md) | 13 | 13 | 22 | 1 | 8 |
| [november](manad/2027-11.md) | 13 | 13 | 22 | 1 | 7 |
| [december](manad/2027-12.md) | 12 | 12 | 21 | 1 | 5 |

## Fält som gäller alla prompter

| Steg | Modell | Fält och val |
|---|---|---|
| Reel steg 1, ansiktslös | Nano Banana Pro | Image · 9:16 · 2K · inga referensbilder · antal 1 |
| Reel steg 1, avatar | Soul 2.0 | Image · Karaktär Mia v1 · stil General · 9:16 · 2K · antal 1 |
| Reel steg 2 | Seedance 2.5 | Video · bild till video (Start frame = startbilden) · 9:16 · 10 s · 1080p · ljud AV · bitrate High · Draft AV |
| Karusellomslag, ansiktslös | Nano Banana Pro | Image · 4:5 · 2K · antal 1 |
| Karusellomslag, avatar | Soul 2.0 | Image · Karaktär Mia v1 · 3:4 (beskärs till 4:5) · 2K |
| Textur | Nano Banana Pro | Image · 4:5 · 2K |

**Reserv om Seedance 2.5 krånglar:** Seedance 2.0 (också Unlim) med samma val plus Mode `std`
och Genre `auto`. Kling 3.0 fungerar också (Start frame, 9:16, 10 s, Mode `pro`, Sound `off`) men
har inte Unlim-märket och drar credits.

**Varför ljudet är av:** Seedance kan skapa eget ljud, ibland röster. Reglerna säger ingen
syntetisk röst, så musiken läggs på i Instagram i stället.

**Varför ingen text i bilden:** videomodeller stavar ofta fel. Därför slutar varje prompt med
"no text, no letters" och raderna läggs på i steg 3.
