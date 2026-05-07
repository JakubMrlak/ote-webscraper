# OTE IDA Scraper

Stahuje výsledky vnitrodenních aukcí IDA1, IDA2, IDA3 z webu OTE, a.s. a ukládá je do `.parquet` souborů.

## Instalace

```bash
git clone https://github.com/JakubMrlak/ote-webscraper.git
cd OTE-WEBSCRAPER
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

## Použití

Stáhnout jednu aukci:
```bash
python -m ote_ida.cli fetch IDA1 2026-04-30
```

Stáhnout rozsah datumů:
```bash
python -m ote_ida.cli fetch-range 2026-04-01 2026-04-30
```

Stáhnout jen vybrané sessions:
```bash
python -m ote_ida.cli fetch-range 2026-04-01 2026-04-30 --sessions IDA1 IDA2
```

## Schéma výstupu

### Intervalová data
`output/ote_ida_aukce/year=YYYY/month=MM/day=DD/{session}/part000.parquet`

| Sloupec | Typ | Popis |
|---|---|---|
| `delivery_date` | date | Datum dodání |
| `session` | string | IDA1, IDA2 nebo IDA3 |
| `interval_start` | datetime[tz] | Začátek intervalu (Europe/Prague) |
| `interval_end` | datetime[tz] | Konec intervalu (Europe/Prague) |
| `price_eur_mwh` | float64 | Cena EUR/MWh |
| `volume_mwh` | float64 | Množství MWh |
| `balance_mwh` | float64 | Saldo MWh |
| `export_mwh` | float64 | Export MWh |
| `import_mwh` | float64 | Import MWh |
| `interval_count_valid` | bool | True pokud počet intervalů odpovídá očekávání |

### Souhrnná data
`output/ote_ida_souhrn/year=YYYY/month=MM/day=DD/{session}/part000.parquet`

| Sloupec | Typ | Popis |
|---|---|---|
| `delivery_date` | date | Datum dodání |
| `session` | string | IDA1, IDA2 nebo IDA3 |
| `type` | string | BASE LOAD, PEAK LOAD, OFFPEAK LOAD |
| `price_eur_mwh` | float64 | Cena EUR/MWh |

## Volba zdroje dat

Scraper stahuje data ve formátu **XLSX** místo HTML scrapingu. Důvody:
- Data jsou přesně strukturovaná bez závislosti na HTML/CSS
- Stabilní URL vzor: `/pubweb/attachments/431/{year}/month{mm}/day{dd}/{session}_{dd}_{mm}_{yyyy}_CZ.xlsx`
- Jednodušší parsování přes `pandas` + `openpyxl`

## Okrajové situace

### Přechody času
- **Jarní přechod** (např. 2025-03-30): IDA1/IDA2 mají 92 intervalů místo 96. Skript to správně detekuje a `interval_count_valid = True` (92 je očekávaný počet pro tento den).
- **Podzimní přechod** (např. 2025-10-26): IDA1/IDA2 mají 100 intervalů. OTE označuje opakující se hodinu jako `02a`/`02b` – skript to správně parsuje a timestamps jsou jednoznačné.
- **IDA3**: Vždy pokrývá 12:00–24:00 = 48 intervalů bez ohledu na DST.

### Chybějící data
- HTTP 404 → WARNING, skript pokračuje
- Timeout → ERROR, skript pokračuje
- Prázdná tabulka → ERROR, skript pokračuje

### Idempotence
Strategie: **přepis souboru**. Opakované spuštění pro stejný den přepíše existující soubor. Důvod: jednoduchá implementace, žádné duplikáty, bezpečný re-run při opravě dat.

## Spuštění testů

```bash
python -m pytest tests/ -v
```

Testy nepoužívají síť – pracují s fixtures uloženými v `tests/fixtures/`.

## Známá omezení

- Scraper nestahuje data starší než 1.1.2024 (zadání)
- Souhrnná data neobsahují množství (BASE/PEAK/OFFPEAK LOAD MWh) – pouze ceny
- Není implementován rate limiting při stahování většího rozsahu datumů