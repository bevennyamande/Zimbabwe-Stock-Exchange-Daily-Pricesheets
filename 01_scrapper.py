import os
from datetime import datetime
import pandas as pd

BASE_URL = "https://www.zse.co.zw/price-sheet/"
DAILY_CSV_DIR = "csv-daily-pricesheets"
DAILY_XLS_DIR = "xls-daily-price-sheets"
CUMULATIVE_CSV = "combined/all_prices.csv"
CUMULATIVE_XLS = "combined/all_prices.xlsx"


def fetch_data_from_url(url):
    try:
        response = pd.read_html(url, skiprows=1)
        dataframe = response[0][3:]
        dataframe.columns = ["Name", "None1", "None2", "Opening_Price", "Closing_Price", "Volume_Traded"]
        df_trades = dataframe[["Name", "Opening_Price", "Closing_Price", "Volume_Traded"]]
        df_trades = df_trades.dropna(how="all").set_index("Name")
        return df_trades
    except Exception as e:
        print(f"[ERROR] Failed to fetch or parse data: {e}")
        return pd.DataFrame()


def current_date_str():
    return datetime.now().strftime("%Y-%m-%d")


def save_daily_files(df, date_str):
    os.makedirs(DAILY_CSV_DIR, exist_ok=True)
    os.makedirs(DAILY_XLS_DIR, exist_ok=True)

    df.to_csv(f"{DAILY_CSV_DIR}/{date_str}.csv")
    df.to_excel(f"{DAILY_XLS_DIR}/{date_str}.xlsx")


def update_cumulative_files(df, date_str):
    os.makedirs("combined", exist_ok=True)

    df = df.copy()
    df["Date"] = date_str
    df.reset_index(inplace=True)

    if os.path.exists(CUMULATIVE_CSV):
        existing = pd.read_csv(CUMULATIVE_CSV)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.drop_duplicates(subset=["Name", "Date"], inplace=True)
    else:
        combined = df

    combined.to_csv(CUMULATIVE_CSV, index=False)
    combined.to_excel(CUMULATIVE_XLS, index=False)


def main():
    date_str = current_date_str()
    df = fetch_data_from_url(BASE_URL)

    if df.empty:
        print("[WARN] No data fetched. Skipping save.")
        return

    save_daily_files(df, date_str)
    update_cumulative_files(df, date_str)
    print(f"[INFO] Data saved for {date_str}")


if __name__ == "__main__":
    main()

