


import os
import pandas as pd
from datetime import datetime

# Directories
DAILY_CSV_DIR = "csv-daily-pricesheets"
DAILY_XLS_DIR = "xls-daily-price-sheets"
CUMULATIVE_CSV = "combined/all_prices.csv"
CUMULATIVE_XLS = "combined/all_prices.xlsx"


def extract_date_from_filename(filename):
    """
    Extract a datetime object from filenames in MM-DD-YYYY format.
    Example: 03-06-2024.csv or 03-06-2024.xlsx
    """
    try:
        return datetime.strptime(filename.split('.')[0], "%m-%d-%Y")
    except ValueError:
        return None


def load_file(filepath, file_type):
    """
    Read a CSV or Excel file into a DataFrame.
    """
    try:
        if file_type == "csv":
            return pd.read_csv(filepath)
        elif file_type == "xlsx":
            return pd.read_excel(filepath)
    except Exception as e:
        print(f"[ERROR] Failed to read {filepath}: {e}")
    return None


def combine_all_existing_files():
    """
    Combine all daily CSV and Excel files into a unified cumulative CSV and Excel file,
    ordered chronologically and deduplicated by Name and Date.
    """
    os.makedirs("combined", exist_ok=True)
    combined_df = pd.DataFrame()

    # --- Collect and sort CSV files ---
    csv_files = [
        f for f in os.listdir(DAILY_CSV_DIR)
        if f.endswith(".csv") and extract_date_from_filename(f)
    ]
    csv_files.sort(key=extract_date_from_filename)

    for f in csv_files:
        date_str = f.replace(".csv", "")
        df = load_file(os.path.join(DAILY_CSV_DIR, f), "csv")
        if df is not None and "Name" in df.columns:
            df["Date"] = date_str
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # --- Collect and sort Excel files ---
    xls_files = [
        f for f in os.listdir(DAILY_XLS_DIR)
        if f.endswith(".xlsx") and extract_date_from_filename(f)
    ]
    xls_files.sort(key=extract_date_from_filename)

    for f in xls_files:
        date_str = f.replace(".xlsx", "")
        df = load_file(os.path.join(DAILY_XLS_DIR, f), "xlsx")
        if df is not None and "Name" in df.columns:
            df["Date"] = date_str
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # --- Final deduplication and save ---
    if not combined_df.empty:
        combined_df.drop_duplicates(subset=["Name", "Date"], inplace=True)
        combined_df.to_csv(CUMULATIVE_CSV, index=False)
        combined_df.to_excel(CUMULATIVE_XLS, index=False)
        print(f"[INFO] Combined total: {len(combined_df)} rows saved to:")
        print(f"       - {CUMULATIVE_CSV}")
        print(f"       - {CUMULATIVE_XLS}")
    else:
        print("[WARN] No valid data found to combine.")


if __name__ == "__main__":
    combine_all_existing_files()

