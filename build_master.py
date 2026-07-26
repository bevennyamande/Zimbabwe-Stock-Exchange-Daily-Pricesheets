#!/usr/bin/env python3
"""
Build master sheets from individual daily XLS files — one per metric.

Reads every daily price sheet from xls_files_grouped_by_month_year/ (or
xls-daily-price-sheets/), extracts the chosen metric for each company, and
builds a unified master CSV:

    Company Name | MM-DD-YYYY | MM-DD-YYYY | ...

Outputs:
  - master_closing_price.csv   — closing price
  - master_volume_traded.csv   — total traded volume
  - master_opening_price.csv   — opening price

Companies are rows, dates are columns.  NaN where a company wasn't listed.
Incremental — only new dates are appended, existing data is never overwritten.

Handles the various file formats used over the years:
  - True .xlsx  (PK header — early files)
  - CSV saved as .xlsx with "Name,Opening_Price,Closing_Price,Volume_Traded"
  - CSV with lowercase headers: ",name,opening,closing,volume"
  - CSV with/without an extra leading index column
  - Files where company names are numeric (unrecoverable — skipped)
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from collections import OrderedDict
from typing import Callable

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "xls_files_grouped_by_month_year"
if not SOURCE_DIR.is_dir():
    SOURCE_DIR = BASE_DIR / "xls-daily-price-sheets"

# Which masters to build:  {canonical_column: filename_slug}
MASTER_SLUGS = OrderedDict([
    ("Closing_Price",  "closing_price"),
    ("Volume_Traded",  "volume_traded"),
    ("Opening_Price",  "opening_price"),
])

# Abbreviated month names for filenames (all-caps, 3 letters)
_MONTH_ABBR = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _format_date_for_filename(date_str: str) -> str:
    """Convert 'MM-DD-YYYY' to 'DD-Mon-YYYY' for use in filenames."""
    dt = parse_date_from_filename(date_str + ".xlsx")
    if dt:
        return f"{dt.day:02d}-{_MONTH_ABBR[dt.month]}-{dt.year}"
    return date_str  # fallback


def _find_existing_master(slug: str) -> Path | None:
    """Find an existing master file for *slug*, regardless of date range."""
    candidates = sorted(BASE_DIR.glob(f"master_{slug}_*.csv"))
    return candidates[-1] if candidates else None

# Canonical column set from scrapper.py
CANONICAL_COLS = ["Name", "Opening_Price", "Closing_Price", "Volume_Traded"]

# ---------------------------------------------------------------------------
# Date helpers  (format is MM-DD-YYYY, with a few DD-MM-YYYY outliers)
# ---------------------------------------------------------------------------

def parse_date_from_filename(filename: str) -> datetime | None:
    """Parse 'MM-DD-YYYY.xlsx' (or DD-MM-YYYY outliers) into a datetime."""
    name = filename.replace(".xlsx", "").replace(".xls", "")
    m = re.match(r"^(\d{2})-(\d{2})-(\d{4})$", name)
    if not m:
        return None
    a, b, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if 1 <= a <= 12:
        month, day = a, b
    elif 1 <= b <= 12:
        month, day = b, a
    else:
        return None
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def _chrono_key(date_str: str) -> str:
    """Sort key: 'MM-DD-YYYY' → 'YYYY-MM-DD'."""
    dt = parse_date_from_filename(date_str + ".xlsx")
    return dt.strftime("%Y-%m-%d") if dt else date_str


# ---------------------------------------------------------------------------
# File parser
# ---------------------------------------------------------------------------

def parse_sheet(filepath: Path, value_column: str) -> dict[str, float]:
    """
    Parse a single daily sheet, returning {company_name: value}.

    *value_column* is one of the canonical column names:
      "Closing_Price" | "Volume_Traded" | "Opening_Price"
    """

    # ── 1. Load raw data ──────────────────────────────────────────────────
    with open(filepath, "rb") as fh:
        is_xlsx = fh.read(2) == b"PK"

    if is_xlsx:
        try:
            df = pd.read_excel(filepath, header=None)
        except Exception:
            return {}
    else:
        try:
            df = pd.read_csv(filepath, header=0)
            if df.empty or len(df.columns) < 2:
                raise ValueError("empty")
        except Exception:
            try:
                df = pd.read_csv(filepath, header=None)
            except Exception:
                return {}

    if df.empty:
        return {}

    # ── 2. Drop fully-empty rows & columns ────────────────────────────────
    df = df.dropna(how="all").dropna(axis=1, how="all")
    if df.empty:
        return {}

    # ── 3. Normalise to canonical columns ─────────────────────────────────
    df = _normalize_columns(df)

    needed = {"Name", value_column}
    if not needed.issubset(df.columns):
        return {}

    # ── 4. Clean rows ─────────────────────────────────────────────────────
    df = df.reset_index(drop=True)
    name_ser = df["Name"].astype(str).str.strip()

    bad_mask = (
        name_ser.str.lower().str.contains("equities", na=False)
        | name_ser.isin(["", "nan", "NaN", "None", "Name", "Company Name"])
        | (name_ser.str.len() <= 2)
        | name_ser.str.match(r"^\d+(\.\d+)?$")
    )
    df = df[~bad_mask]

    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")
    df = df.dropna(subset=[value_column])

    if df.empty:
        return {}

    # ── 5. Build result ───────────────────────────────────────────────────
    result: dict[str, float] = OrderedDict()
    for _, row in df.iterrows():
        name = str(row["Name"]).strip()
        val = float(row[value_column])
        if name and len(name) > 2:
            result[name] = val

    return result


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise a DataFrame to canonical [Name, Opening_Price, Closing_Price, Volume_Traded]."""
    # ── Detect & promote header row ────────────────────────────────────────
    first_row = df.iloc[0].astype(str).str.strip()
    if first_row.str.lower().str.contains(
        "closing|opening|volume|traded|company|name", na=False
    ).any():
        df.columns = [str(c).strip() for c in first_row]
        df = df.iloc[1:].reset_index(drop=True)

    # ── Map known variants to canonical names ──────────────────────────────
    rename: dict[str, str] = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if c in ("name", "company name", "company") or "company_name" in c:
            rename[col] = "Name"
        elif "opening" in c or c == "open" or "opening_price" in c:
            rename[col] = "Opening_Price"
        elif "closing" in c or c == "close" or "closing_price" in c:
            rename[col] = "Closing_Price"
        elif "volume" in c or c == "traded" or "volume_traded" in c:
            rename[col] = "Volume_Traded"

    if rename:
        df = df.rename(columns=rename)
        keep = [c for c in CANONICAL_COLS if c in df.columns]
        if keep:
            return df[keep]

    # ── Positional heuristic (no recognisable headers) ────────────────────
    ncol = len(df.columns)
    name_idx: int | None = None
    for i in range(min(4, ncol)):
        alpha = df.iloc[:, i].dropna().astype(str).str.match(
            r"^[A-Za-z .&(),-]{4,}$", na=False
        ).sum()
        if alpha >= 3:
            name_idx = i
            break

    if name_idx is None:
        best, best_i = 0, 0
        for i in range(ncol):
            cnt = df.iloc[:, i].dropna().astype(str).str.match(
                r"^[A-Za-z]", na=False
            ).sum()
            if cnt > best:
                best, best_i = cnt, i
        if best >= 3:
            name_idx = best_i
        else:
            return pd.DataFrame()

    num_cols = []
    for i in range(ncol):
        if i == name_idx:
            continue
        s = pd.to_numeric(df.iloc[:, i], errors="coerce")
        if s.notna().sum() >= 2:
            num_cols.append(i)
    num_cols.sort(key=lambda i: abs(i - name_idx))

    result = pd.DataFrame()
    result["Name"] = df.iloc[:, name_idx].astype(str).str.strip()
    for canon_label, idx in zip(CANONICAL_COLS[1:], num_cols):
        result[canon_label] = pd.to_numeric(df.iloc[:, idx], errors="coerce")
    return result


# ---------------------------------------------------------------------------
# Master builder
# ---------------------------------------------------------------------------

def build_one_master(slug: str, value_column: str) -> None:
    """Build or update a single master CSV for *value_column*.

    The output filename is:
        master_{slug}_{start-date}_to_{end-date}.csv
    e.g. master_closing_price_11-Jan-2020_to_16-Jun-2025.csv

    If an older master with a different date range exists, it is loaded,
    merged, saved with the new name, and the old file is removed.
    """
    all_files = sorted(
        [f for f in SOURCE_DIR.rglob("*.xlsx") if f.is_file()],
        key=lambda f: _chrono_key(f.name.replace(".xlsx", "")),
    )
    if not all_files:
        print(f"  [SKIP] No files found.")
        return

    # ── Load existing master (may have old date range in filename) ───────────
    old_path = _find_existing_master(slug)
    if old_path:
        master = pd.read_csv(old_path, index_col=0, dtype=str)
        master = master.apply(lambda col: pd.to_numeric(col, errors="coerce"))
        existing_dates = set(master.columns)
    else:
        master = pd.DataFrame()
        existing_dates = set()
        old_path = None

    # ── Parse every file ─────────────────────────────────────────────────────
    new_data: dict[str, dict[str, float]] = OrderedDict()
    skipped = 0
    failed = 0

    for fp in all_files:
        date_str = fp.name.replace(".xlsx", "").replace(".xls", "")
        if date_str in existing_dates:
            skipped += 1
            continue

        try:
            row = parse_sheet(fp, value_column)
        except Exception:
            failed += 1
            continue

        if row:
            new_data[date_str] = row
        else:
            failed += 1

    label = value_column.replace("_", " ").title()
    print(
        f"  New: {len(new_data)}  |  "
        f"Skipped: {skipped}  |  "
        f"Unparsed: {failed}"
    )

    if not new_data:
        print(f"  [{label}] up to date.")
        return

    # ── Merge ────────────────────────────────────────────────────────────────
    sorted_dates = sorted(new_data.keys(), key=_chrono_key)
    new_df = pd.DataFrame(new_data).reindex(columns=sorted_dates)
    new_df.index.name = "Company"

    if master.empty:
        master = new_df
    else:
        master = master.combine_first(new_df)
        for col in sorted_dates:
            if col not in master.columns:
                master[col] = new_df[col]

    all_dates = sorted(master.columns, key=_chrono_key)
    master = master.reindex(columns=all_dates).sort_index()
    master.index.name = "Company"

    first_date = _format_date_for_filename(all_dates[0])
    last_date = _format_date_for_filename(all_dates[-1])

    new_path = BASE_DIR / f"master_{slug}_{first_date}_to_{last_date}.csv"

    # ── Save ─────────────────────────────────────────────────────────────────
    master.to_csv(new_path, float_format="%.4f")

    # Remove old file if the name changed
    if old_path and old_path.resolve() != new_path.resolve():
        old_path.unlink()

    print(
        f"  [{label}] Saved: {new_path.name}\n"
        f"    {len(master)} companies × {len(master.columns)} days  "
        f"({first_date} → {last_date})"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not SOURCE_DIR.is_dir():
        print(f"[ERROR] Source directory not found: {SOURCE_DIR}")
        sys.exit(1)

    total = sum(1 for _ in SOURCE_DIR.rglob("*.xlsx"))
    print(f"Source files: {total}\n")

    for value_col, slug in MASTER_SLUGS.items():
        label = value_col.replace("_", " ").title()
        print(f"── {label} ──")
        build_one_master(slug, value_col)
        print()


if __name__ == "__main__":
    main()
