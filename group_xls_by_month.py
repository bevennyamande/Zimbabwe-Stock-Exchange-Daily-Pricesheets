#!/usr/bin/env python3
"""
Group XLS daily price sheets by month-year and copy them into a structured
directory tree.

Source:  xls-daily-price-sheets/
Target:  xls_files_grouped_by_month_year/MMM-YYYY/

The naming convention is MM-DD-YYYY (confirmed by scrapper.py's %m-%d-%Y),
with a handful of older files (2020–2021) using DD-MM-YYYY. This script
handles both: if the first token is 13–31 it's a day, so we read the second
token as the month instead.

Safe to run daily — only copies files that haven't been placed yet.
"""

import shutil
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "xls-daily-price-sheets"
TARGET_DIR = BASE_DIR / "xls_files_grouped_by_month_year"

# Loose match — we validate month/day ranges ourselves below
MONTH_ABBR = {
    1: "JAN", 2: "FEB", 3: "MAR", 4: "APR",
    5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG",
    9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC",
}

FILENAME_RE = re.compile(
    r"^(?P<a>\d{2})-(?P<b>\d{2})-(?P<year>\d{4})\.xlsx?$",
    re.IGNORECASE,
)


def _parse_month_year(filename: str) -> str | None:
    """Return 'MM-YYYY' for *filename*, or None if it can't be parsed."""
    m = FILENAME_RE.match(filename)
    if not m:
        return None

    a = int(m.group("a"))   # first token
    b = int(m.group("b"))   # second token
    year = m.group("year")

    # Heuristic: if the first token is a valid month (01–12) we treat the
    # format as MM-DD-YYYY.  Otherwise (13–31) it must be a day, so the
    # format is DD-MM-YYYY and the month is the *second* token.
    if 1 <= a <= 12:
        month = a
    elif 1 <= b <= 12:
        month = b
    else:
        return None  # neither token is a valid month — can't group

    return f"{MONTH_ABBR[month]}-{year}"


def group_and_copy() -> None:
    """Scan source, group by MM-YYYY, copy new files into target."""
    if not SOURCE_DIR.is_dir():
        print(f"[ERROR] Source directory not found: {SOURCE_DIR}")
        return

    xls_files = sorted(
        f for f in SOURCE_DIR.iterdir() if f.is_file() and f.suffix.lower() in {".xls", ".xlsx"}
    )

    if not xls_files:
        print("[INFO] No XLS files found.")
        return

    stats = {"created": 0, "copied": 0, "skipped": 0, "errors": 0, "unparsed": 0}

    for file_path in xls_files:
        month_year = _parse_month_year(file_path.name)

        if month_year is None:
            stats["unparsed"] += 1
            print(f"[WARN] Skipping — can't determine month: {file_path.name}")
            continue

        dest_dir = TARGET_DIR / month_year

        if not dest_dir.is_dir():
            dest_dir.mkdir(parents=True, exist_ok=True)
            stats["created"] += 1

        dest_path = dest_dir / file_path.name

        if dest_path.exists():
            stats["skipped"] += 1
            continue

        try:
            shutil.copy2(file_path, dest_path)
            stats["copied"] += 1
        except OSError as exc:
            stats["errors"] += 1
            print(f"[ERROR] {file_path.name}: {exc}")

    # ── Summary ──────────────────────────────────────────────────────────
    parts = [
        f"Subfolders created: {stats['created']}",
        f"Files copied: {stats['copied']}",
        f"Already up-to-date: {stats['skipped']}",
    ]
    if stats["unparsed"]:
        parts.append(f"Skipped (unparsed): {stats['unparsed']}")
    if stats["errors"]:
        parts.append(f"Errors: {stats['errors']}")

    print("\nDone. " + " | ".join(parts))


if __name__ == "__main__":
    group_and_copy()
