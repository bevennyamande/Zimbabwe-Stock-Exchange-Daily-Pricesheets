[![Scrapper application](https://github.com/bevennyamande/Zimbabwe-Stock-Exchange-Daily-Pricesheets/actions/workflows/github-actions-scrapper.yml/badge.svg)](https://github.com/bevennyamande/Zimbabwe-Stock-Exchange-Daily-Pricesheets/actions/workflows/github-actions-scrapper.yml)

# Zimbabwe Stock Exchange — Daily Price Sheets

> **Project status: Archived (July 2026)**
>
> Data collected from **11 January 2020** through **16 June 2025** —
> 1,032 trading days across 63 ZSE-listed companies.

---

## The Dataset

**Metrics:** Opening price, closing price, total traded volume.

### Master sheets

| File | Description |
|---|---|
| [`master_closing_price_11-Jan-2020_to_16-Jun-2025.csv`](master_closing_price_11-Jan-2020_to_16-Jun-2025.csv) | Closing prices (companies × dates) |
| [`master_volume_traded_11-Jan-2020_to_16-Jun-2025.csv`](master_volume_traded_11-Jan-2020_to_16-Jun-2025.csv) | Traded volumes |
| [`master_opening_price_11-Jan-2020_to_16-Jun-2025.csv`](master_opening_price_11-Jan-2020_to_16-Jun-2025.csv) | Opening prices |

All three are structured as **companies × dates** matrices — companies as rows,
trading days (`MM-DD-YYYY`) as columns.

### Raw files

- [`xls-daily-price-sheets/`](xls-daily-price-sheets/) — 1,057 daily sheets
- [`xls_files_grouped_by_month_year/`](xls_files_grouped_by_month_year/) — same sheets, grouped into `MMM-YYYY` folders
- [`csv-daily-pricesheets/`](csv-daily-pricesheets/) — CSV mirror

---

## Tools

| Script | Purpose |
|---|---|
| `group_xls_by_month.py` | Copies daily sheets into `MMM-YYYY` subfolders |
| `build_master.py` | Rebuilds the three master CSVs from daily sheets |
| `scrapper.py` | Original scraper (deprecated — kept for reference) |

---

## Disclaimer

This dataset is provided for **informational and educational purposes only**
and does not constitute financial, investment, or trading advice.

---
