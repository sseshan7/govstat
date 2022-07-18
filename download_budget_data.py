import requests
from bs4 import BeautifulSoup
import os

BUDGET_DATA_URL = "https://www.whitehouse.gov/omb/budget/historical-tables/"

def download_xlsx_data(url: str = BUDGET_DATA_URL) -> None:
    """
    Downloads all of the xlsx files in the a tag from a given URL.
    It assumes a year, month, and files name from the xlsx link.
    """
    page = requests.get(BUDGET_DATA_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    links = soup.find_all('a', href=True)
    for sec in links:
        print(sec)
        link = sec['href']
        if link.endswith(".xlsx"):
            r = requests.get(link, allow_redirects=True)
            link_split = link.split('/')
            file_name = link_split[-1]
            month = link_split[-2]
            year = link_split[-3]
            file_path = os.path.join('data', year, month, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            open(file_path, 'wb').write(r.content)

if __name__ == "__main__":
    download_xlsx_data()
