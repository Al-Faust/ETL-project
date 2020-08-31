from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import requests
import json
import pandas as pd
import datetime
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape1():
    #start browser and visit item id page (currently using Fire rune as test)
    browser = init_browser()
    url = f'http://www.itemdb.biz/index.php?search=fire+rune'
    browser.visit(url)

    #pause for load
    #time.sleep(5)

    # scrape page into soup
    html = browser.html
    soup = bs(html, 'html.parser')

    #locate item id and name
    table_row = soup.find_all('tbody')
    item_dict = {}
    for th in table_row:
        item_id = th.find('td').text
        item_name = th.find('td').next_element.next_element.next_element.next_element.next_element
        item_dict = {
            'item_name':item_name,
            'item_id': item_id 
        }
    #time.sleep(5)
    browser.quit()

    #get id and plug into api
    newid = item_dict['item_id']
    gen_url = f'https://secure.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item={newid}'
    gen_response = requests.get(gen_url)
    gen_json = gen_response.json()

    #generate df
    gen_df = pd.DataFrame()

    #get gen info into variables
    itemid = gen_json['item']['id']
    name = gen_json['item']['name']
    small_icon_url = gen_json['item']['icon']
    large_icon_url = gen_json['item']['icon_large']
    current_price = gen_json['item']['current']
    short_delta = gen_json['item']['day30']
    med_delta = gen_json['item']['day90']
    long_delta = gen_json['item']['day180']

    #remove weird characters in price, change over time variables and add to gen df
    if type(current_price['price']) == int:
        gen_df['id'] = [itemid]
        gen_df['name'] = [name]
        gen_df['current_price'] = [current_price['price']]
        gen_df['_30_day_change'] = [short_delta['change'].strip('+%')]
        gen_df['_90_day_change'] = [med_delta['change'].strip('+%')]
        gen_df['_180_day_change'] = [long_delta['change'].strip('+%')]
        gen_df['small_icon_url'] = [small_icon_url]
        gen_df['large_icon_url'] = [large_icon_url]
    else:
        gen_df['id'] = [itemid]
        gen_df['name'] = [name]
        gen_df['current_price'] = [current_price['price'].replace(',','')]
        gen_df['_30_day_change'] = [short_delta['change'].strip('+%')]
        gen_df['_90_day_change'] = [med_delta['change'].strip('+%')]
        gen_df['_180_day_change'] = [long_delta['change'].strip('+%')]
        gen_df['small_icon_url'] = [small_icon_url]
        gen_df['large_icon_url'] = [large_icon_url]

    gen_json = gen_df.to_json(orient="records")
    return gen_json

def scrape2():
    #start browser and visit item id page (currently using Fire rune as test)
    browser = init_browser()
    url = f'http://www.itemdb.biz/index.php?search=fire+rune'
    browser.visit(url)

    #pause for load
    #time.sleep(5)

    # scrape page into soup
    html = browser.html
    soup = bs(html, 'html.parser')

    #locate item id and name
    table_row = soup.find_all('tbody')
    item_dict = {}
    for th in table_row:
        item_id = th.find('td').text
        item_name = th.find('td').next_element.next_element.next_element.next_element.next_element
        item_dict = {
            'item_name':item_name,
            'item_id': item_id 
        }
    #time.sleep(5)
    browser.quit()

    newid = item_dict['item_id']
    graph_url = f'http://services.runescape.com/m=itemdb_rs/api/graph/{newid}.json'
    graph_response = requests.get(graph_url)
    graph_json = graph_response.json()
    graph_daily = graph_json['daily']

    #generate df
    daily_graph_df = pd.DataFrame()

    #separate daily keys and values into 2 lists
    daily_keys = graph_daily.keys()
    daily_values = graph_daily.values()
    correct_daily_keys = []
    correct_daily_value = []

    #apply timestamp mod and add new keys to list
    for key in daily_keys:
        timestamp = datetime.datetime.fromtimestamp(( int(key) / 1000)).strftime('%m.%d.%Y')
        correct_daily_keys.append(timestamp)

    #add new values to list
    for value in daily_values:
        correct_daily_value.append(value)

    #add to daily graph df
    daily_graph_df['Date'] = correct_daily_keys
    daily_graph_df['price'] = correct_daily_value
    daily_graph_json = daily_graph_df.to_json(orient="records")

    return daily_graph_json