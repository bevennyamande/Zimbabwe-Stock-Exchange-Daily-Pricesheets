# this program is for educational purposes only
import requests
import re
from bs4 import BeautifulSoup

html_page = requests.get('http://wwww.zimbabwe-stock-exchange.com/downloads/zse/#prices')
soup = BeautifulSoup(html_page.content)
soup = soup.prettify()
#string = r"http://wwww.zimbabwe-stock-exchange.com/External.asp?L=I&from=du&ID=64996&B=2104"
string = r"^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$"


for line in soup:
    if line == re.search(string,soup):
        print(line)
