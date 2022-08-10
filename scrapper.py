import os
from datetime import datetime
import pandas as pd


BASE_URL = "https://www.zse.co.zw/price-sheet/"


def fetch_data_from_url(url):
    """
    Fetch the market prices from the Zimbabwe Stock Exchange Website
    """
    try:
        response = pd.read_html(url, skiprows=1)

    except Exception as e:
        pass

    dataframe = response[0][4:]
    # The response has 8 columns but only concerned with few
    dataframe.columns = [
        "Name",
        "None",
        "None",
        "None",
        "None",
        "Opening_Price",
        "Closing_Price",
        "Volume_Traded",
    ]
    # Lets filter the columns we are concerned with
    df_trades = dataframe[["Name", "Opening_Price", "Closing_Price", "Volume_Traded"]]

    # Drop all the columns with no data or missing all data
    dataframe = df_trades.dropna(how="all").set_index('Name')
    return dataframe


def current_date():
    """
    Generate the current date for use in saving the price sheet
    """
    now = datetime.now()
    current_date = now.strftime("%m-%d-%Y")
    return current_date


def check_or_create_directory(dataframe, current_date):
    """
    Create or save in the folder with other files
    """
    os.makedirs("csv-daily-pricesheets", exist_ok=True)
    # Save the data into both the CSV and Excel folders
    dataframe.to_csv(f"csv-daily-pricesheets/{current_date}.csv")
    dataframe.to_csv(f"xls-daily-price-sheets/{current_date}.xlsx")


def main():
    dataframe = fetch_data_from_url(BASE_URL)
    check_or_create_directory(dataframe, current_date())


if __name__ == "__main__":
    main()
