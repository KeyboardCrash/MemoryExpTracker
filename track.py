from concurrent.futures.process import _threads_wakeups
import random
from bs4 import BeautifulSoup
import sys
import requests
import time
from threading import Thread
import config

productList = dict()
productData = []
tempData = []
cacheTime = 0

# Find all of the products we're looking for
def setup():

    numPages = config.DevelopmentConfig.NUM_OF_PAGES
    url = config.DevelopmentConfig.SCRAPE_URL

    try:
        records = BeautifulSoup('', 'html.parser')
        # Iterate over the pages on the website
        for page in range(1, numPages):
            pagecontent = requests.get(url + '&Page=' + str(page))
            soup = BeautifulSoup(pagecontent.content, 'html.parser')
            a = soup.find_all('div', 'c-shca-icon-item__body-name')
            records.extend(a)

        for record in records:
            redirect = record.find('a', href=True)
            url = redirect['href']

            product = record.find('a')
            name = product.text
            name = ' '.join(name.split())

            productList[url] = name
        
        # print(productList)
        log('number of products found: ' + str(len(productList)))
    except Exception as e:
        print('exception hit in setup', e)


def parseInventory(url, productName):
    try:
        global tempData

        pagecontent = requests.get(url)
        soup = BeautifulSoup(pagecontent.content, 'html.parser')

        regions = soup.find_all('li', attrs={'data-role' : 'region'})

        storeObj = {}
        storeObj[productName] = {}

        # Parse regions
        for region in regions:
            regionName = region.find('div', attrs={'data-role' : 'region-title'}).text.strip()
            storeObj[productName][regionName] = []
            storesInRegion = region.find_all('ul', 'c-shco-list--unstyled')
            # Find all stores in region
            for stores in storesInRegion:
                allLocalStores = stores.find_all('div', 'c-capr-inventory-store')
                # Get stock from each store
                for localStore in allLocalStores:
                    stock = localStore.find('span', 'c-capr-inventory-store__availability').text.strip()
                    storeName = localStore.find('span', 'c-capr-inventory-store__name').text.strip()
                    storeObj[productName][regionName].append({"store": storeName, "stock": stock})
        # print(productData)

        # Add to array
        tempData.append(storeObj)

    except Exception as e:
        print('exception hit in parsing', e)
    except KeyboardInterrupt:
        print("Ctrl+C pressed...")
        sys.exit(1)

def log(string):
    print(time.strftime('[%H:%M:%S]'), string)

def get_data():
    mainUrl = 'https://www.memoryexpress.com/'
    
    global productData
    global tempData

    # Clear temp
    tempData.clear()

    ind = 1
    threads = []

    header = {
        "scrape_time": time.ctime()
    }
    tempData.append(header)

    # Parse data of each product
    for key in productList:
        path = key
        name = productList[key]

        # print(path, name)
        print('Scraping #', ind, '/', len(productList), 'product', key, end='\r')

        url = mainUrl + path
        thread = Thread(target = parseInventory, daemon=True, args=(url, name))
        threads.append(thread)
        thread.start()
        ind += 1

    
    for thread in threads:
        while thread.is_alive():
            thread.join(1)
    print('\r\n')

def generate():
    thread = Thread(target=scrape_product, daemon=True, args=())
    thread.start()
    log('Scraper thread started')

def scrape_product():
    global cacheTime
    global productData
    global tempData
    setup()

    while True:
        if (time.time() - cacheTime) > 300:
            log("Cache expiring, pulling new data")
            t = Thread(target=get_data, daemon=True, args=())
            t.start()
            t.join()

            productData.clear()
            for item in tempData:
                productData.append(item)

            log("Cache renewed")
            cacheTime = time.time()

        time.sleep(5)

generate()