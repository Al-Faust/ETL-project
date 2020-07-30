from splinter import Browser
from bs4 import BeautifulSoup as bs
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_ids():
    browser = init_browser()

    url = f'http://www.itemdb.biz/index.php?search=fire+rune'
    init_browser().visit(url)

    time.sleep(1)

    # scrape page into soup
    html = browser.html
    soup = bs(html, 'html.parser')

    table_row = soup.find_all('tbody')

    for th in table_row:
        item_id = th.find('td').text
        item_name = th.find('td').next_element.next_element.next_element.next_element.next_element
        item_dict = {
        'item_name':item_name,
        'id': item_id
        }
        print(item_dict)

    browser.quit()

    return item_dict

   # next button is paginate_button next
