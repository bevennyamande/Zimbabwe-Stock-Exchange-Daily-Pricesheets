import os
from datetime import datetime
import pandas as pd


BASE_URL = "https://www.zse.co.zw/price-sheet/"


def main():
	try:

		dataframe = pd.read_html(BASE_URL, skiprows=1)
		df = dataframe[0]
		#  Drop all missing values if any
		df.dropna(inplace=True)
		# only get the four columns and discard the first

		df = df.iloc[::,1:]

		# Only interested in the Name, Opening, Closing, Volume Labels
		df.columns = ['name', 'opening', 'closing', 'volume']

		now = datetime.now() # current date and time
		current_date = now.strftime("%m-%d-%Y")

		# Create or check if the folder exists
		os.makedirs('csv-daily-pricesheets', exist_ok=True)

		# Save the data into both the CSV and Excel folders
		df.to_csv(f'csv-daily-pricesheets/{current_date}.csv')  
		df.to_csv(f'xls-daily-price-sheets/{current_date}.xlsx')

	except Exception as e:
		print(e)


if __name__ == '__main__':
	main()
