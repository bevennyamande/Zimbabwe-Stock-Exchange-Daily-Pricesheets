import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv # Import load_dotenv

load_dotenv() # Load environment variables from .env file

BASE_URL = os.getenv("ZSE_BASE_URL")

def fetch_data_from_url(url):
    """
    Fetch the market prices from the Zimbabwe Stock Exchange Website
    """
    try:
        response = pd.read_html(url, header=0)

        dataframe = response[0].copy()

        dataframe.columns = [
            "Name",
            "Opening_Price",
            "Closing_Price",
            "Volume_Traded",
        ]

        df_trades = dataframe[
            ["Name", "Opening_Price", "Closing_Price", "Volume_Traded"]
        ]

        dataframe = df_trades.dropna(how="all").set_index("Name")
        return dataframe

    except Exception as e:
        print(f'Exception occurred {e}')
        return pd.DataFrame()  # Return an empty DataFrame on failure



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
    df = fetch_data_from_url(BASE_URL)
    check_or_create_directory(df, current_date())


if __name__ == "__main__":
    main()
