# this program is for educational purposes only
import requests
import re
from bs4 import BeautifulSoup

html_page = requests.get('http://wwww.zimbabwe-stock-exchange.com/downloads/zse/#prices')
soup = BeautifulSoup(html_page.content)
soup = soup.prettify()
urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', soup)



for line in soup:
    if line == urls:
        print(line)
