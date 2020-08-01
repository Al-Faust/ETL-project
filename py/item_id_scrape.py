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

def scrape():
    #start browser and visit item id page (currently using Fire rune as test)
    browser = init_browser()
    url = f'http://www.itemdb.biz/index.php?search=fire+rune'
    init_browser().visit(url)

    #pause for load
    time.sleep(5)

    # scrape page into soup
    html = browser.html
    soup = bs(html, 'html.parser')

    #locate item id and name
    table_row = soup.find_all('tbody')
    for th in table_row:
        item_id = th.find('td').text
        item_name = th.find('td').next_element.next_element.next_element.next_element.next_element
        item_dict = {
        'item_name':item_name,
        'id': item_id
        }
    browser.quit()

    #get id and plug into api
    id = item_dict['id']
    gen_url = f'https://secure.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item={id}'
    gen_response = requests.get(gen_url)
    gen_json = gen_response.json()

    graph_url = f'http://services.runescape.com/m=itemdb_rs/api/graph/{id}.json'
    graph_response = requests.get(graph_url)
    graph_json = graph_response.json()
    graph_daily = graph_json['daily']

    #generate df
    gen_df = pd.DataFrame()
    daily_graph_df = pd.DataFrame()

    #get gen info into variables
    id = gen_json['item']['id']
    name = gen_json['item']['name']
    small_icon_url = gen_json['item']['icon']
    large_icon_url = gen_json['item']['icon_large']
    current_price = gen_json['item']['current']
    short_delta = gen_json['item']['day30']
    med_delta = gen_json['item']['day90']
    long_delta = gen_json['item']['day180']

    #remove weird characters in price, change over time variables and add to gen df
    if type(current_price['price']) == int:
        gen_df['id'] = [id]
        gen_df['name'] = [name]
        gen_df['current_price'] = [current_price['price']]
        gen_df['_30_day_change'] = [short_delta['change'].strip('+%')]
        gen_df['_90_day_change'] = [med_delta['change'].strip('+%')]
        gen_df['_180_day_change'] = [long_delta['change'].strip('+%')]
    else:
        gen_df['id'] = [id]
        gen_df['name'] = [name]
        gen_df['current_price'] = [current_price['price'].replace(',','')]
        gen_df['_30_day_change'] = [short_delta['change'].strip('+%')]
        gen_df['_90_day_change'] = [med_delta['change'].strip('+%')]
        gen_df['_180_day_change'] = [long_delta['change'].strip('+%')]

    #separate daily keys and values into 2 lists
    daily_keys = graph_daily.keys()
    daily_values = graph_daily.values()
    correct_daily_keys = []
    correct_daily_value = []

    #apply timestamp mod and add new keys to list
    for key in daily_keys:
        timestamp = datetime.datetime.fromtimestamp(( int(key) / 1000)).strftime('%m/%d/%Y')
        correct_daily_keys.append(timestamp)

    #add new values to list
    for value in daily_values:
        correct_daily_value.append(value)

    #add to daily graph df
    daily_graph_df['Date'] = correct_daily_keys
    daily_graph_df['price'] = correct_daily_value

    #sql connection
    connection_string = 'postgres:nwyfre@localhost:5432/osrs_ge_tracker_db'
    engine = create_engine(f'postgresql://{connection_string}')

    #update sql tables
    gen_df.to_sql(name='temp_holding', con=engine, if_exists='replace', index=False)
    daily_graph_df.to_sql(name='price_over_time', con=engine, if_exists='replace', index=False)
    conn = engine.connect()
    trans = conn.begin()

    try:
        engine.execute('delete from general_info where id in(select id from temp_holding)')
        
        gen_df.to_sql(name='general_info', con=engine, if_exists='append', index=False)

    except:
        trans.rollback()
        raise

    #create value over time chart and save
    plt.plot(daily_graph_df['Date'], daily_graph_df['price'])
    plt.title(f'{name} value over time')
    plt.ylabel('GP')
    axes = plt.gca()
    axes.yaxis.grid()
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    plt.show
    plt.savefig('img/valueovertime.png')

    return gen_df, daily_graph_df
