#! /usr/bin/python3

import os
from datetime import date
import pandas as pd
import git
from git import Git

URL = "https://www.zse.co.zw/price-sheet/"


def get_todays_pricesheet(URL: str):
    """ Get the price sheet from the website """

    dataframe = pd.read_html(URL)
    return dataframe

def get_todays_date() -> str:
    """ Get todays date """

    today_date = date.today()
    return today_date.strftime("%d-%m-%Y") # dd-mm-YY

def set_todays_filename() ->str:
    """ Name to save the excel file """

    return './pricesheets/{}.xlsx'.format(get_todays_date())

def main():
    df = get_todays_pricesheet(URL)
    df[0].to_excel(set_todays_filename(), header=True, index=False)

if __name__ == "__main__":
    main()
