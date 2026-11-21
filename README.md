# The World Today: 21 November 2026

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/henahenah31-art/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/henahenah31-art/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

A program that draws one newspaper front page summing up the world's news
of Saturday 21 November 2026, and writes it to `/output/entry.png`.

makefun anchor 6f78051b43408070770d12b6c516101947a19285 round 34141363

## The day in one image — round 1: 38 stories

An early edition: the page was built from news reported up to about
03:00 UTC (10:00 WIB) on Saturday 21 November 2026, so it leans on the
stories that were already out by then — COP31 running into Saturday
overtime, the morning after Cyclone Akvan, and Saturday-morning news
from Australia and India. Every story on the page happened, or was
first reported, on 21 November 2026; the footer says so plainly.

### Main stories (8)

- **COP31 spills into Saturday overtime** — Antalya, 21 Nov: talks miss
  the Friday deadline; nearly 200 nations negotiate on into Saturday,
  split over fossil-fuel language and the "35 by 35" goal.
- **Akvan: the morning after** — Odisha, 21 Nov: rain lingers, relief
  teams clear roads and restore power; schools shut through today,
  fishermen told to stay ashore. Landfall was Friday; 372,000 evacuated,
  no deaths reported.
- **Boy, 3, killed at holiday park** — NSW Central Coast, 21 Nov: a
  three-year-old dies after being hit by a car at a caravan park on
  Saturday morning.
- **Teens hurt in saw-blade mall fight** — Australia, 21 Nov: teenagers
  rushed to hospital after circular saw blades are used in a fight at a
  shopping centre.
- **Three nations, one APEC message** — 21 Nov: Australia, Canada and
  New Zealand issue a joint APEC statement, dated 21 November 2026.
- **Xavier: gale warning narrowed** — 21 Nov: a new marine warning
  (03:34) shrinks the area of gale-force winds from Storm Xavier.
- **Exam results day in India** — 21 Nov: IBPS PO mains result status
  posted; NEET PG 2026 round-two provisional allotment released.
- **India's energy day** — 21 Nov: coal auctions draw 85 bids for 18
  blocks; atomic regulator clears a 700 MW Rajasthan reactor; NLC
  India Renewables files a Rs 3,300-crore IPO.

### Briefs (30)

COP31 fossil-fuel bloc and dropped finance target; the Caretta mascot
dismantled backstage; Akvan rain alerts, 423 rescue teams, 209 mm at
Patrapur; day three of the Wellington Test (India 159/1 overnight);
Las Vegas GP qualifying tonight; Nepal's PM flies to Delhi tomorrow;
Pakistan's climate minister at the SCO forum; Japanese live-fire
drills in India, a first; REC awards, NHPC merger, POWERGRID stake
sale, CERC 1,050 MW clearance, Tata Power safety notices; fuel excise,
biodiesel 0.08%, BS-VI certificates, crude bill $19.5bn; DVC painting
contest; Australian bird flu, smelter rescue, David Jones job cuts,
"dawn-maxxing", Elton John, Medicare breach review; Hyundai hybrid
tech at the LA Auto Show; ASX worst week since Covid; wreck of the
first Australian warship found — plus a "BY THE NUMBERS" footer strip.

### Left out on purpose (date discipline)

Checked and excluded because each happened or was first reported on
20 November (or earlier), not 21 November: Russian missiles landing
in Poland; the ICJ ruling that Myanmar committed genocide; the UK-EU
deals; the Shenzhen Trump-Xi-Putin summit; the Wall Street sell-off
into correction; GTA VI's $3.79bn day-one sales; Bolsonaro's
hospitalisation; the NSE becoming the world's 5th-largest exchange;
the WFP's $12bn food-aid appeal; the Sydney ISIS car-bomb plot
charges; the AFP's 660 kg cocaine seizure; the Kuno cheetah cubs;
the Kryvyi Rih toll (2 dead, 42 hurt); the daraxonrasib cancer-pill
results; the JPMorgan/Visa/Mastercard breach disclosures; the firing
of the US cyber director; Malaysia's Rohingya resettlement plan; the
UN's $52m education fund; the Nepal PM visit announcement; the
Indonesia fires $30.9bn estimate (October data); the Estonia border
closure; and the Carlsen forfeits (19 November).

## How to run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024x1024 PNG, under 1 MiB). Set
`MAKEFUN_OUTPUT_DIR` (or `ENTRY_OUTPUT`) to write somewhere else
instead.

## How it works

Pure Python 3 standard library only (math, os, struct, sys, zlib) — no
network, no clock, no randomness, no third-party imaging, no font files.
The program draws the page with its own layout code, its own 5x7 bitmap
font, and its own PNG encoder (zlib + struct): a masthead,
a lead story with a drawn globe and thermometer, seven more main
stories with hand-drawn icons (cyclone, caravan, saw, flags, waves,
exam paper, lightning bolt), a two-column briefs section, a
"BY THE NUMBERS" strip and a footer stating the coverage window.
Running it twice produces a byte-identical PNG (verified:
sha256 `f07266ae9842ed80be7813887c64754939ce1d07d8a0243e52a2097c66606092`,
37,894 bytes).

## License

MIT — see `LICENSE`.
