import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import urllib.request
import json
import base64
import hmac

import os

coin = "etc"

#170961
os.system("clear")

APIURL = "https://api-swap-rest.bingbon.pro"
APIKEY = "BD8WFvITsvEbsnENQn7OkPOfZd1LjyzquqLLTGbd1v62Lr96"
SECRETKEY = "knlrqI0bs2QbfmkeaWaSh1yinV8sIAFQAT9yTJjtwWu4eDJQ5MbQeKG8LMCEanRz"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument('--disable-gpu')
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
wd = webdriver.Chrome(options=chrome_options)
wd2 = webdriver.Chrome(options=chrome_options)
wd.get('https://www.binance.com/zh-TW/futures/ETCUSDT')
wd2.get('https://swap.bingx.com/en-us/'+coin.upper()+'-USDT')
price = 0

def genSignature(path, method, paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr = method + path + paramsStr
    return hmac.new(SECRETKEY.encode("utf-8"), paramsStr.encode("utf-8"), digestmod="sha256").digest()

def post(url, body):
    req = urllib.request.Request(url, data=body.encode("utf-8"), headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req).read()

def getBalance():
    paramsMap = {
        "apiKey": APIKEY,
        "timestamp": int(time.time()*1000),
        "currency": "USDT",
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/user/getBalance", "POST", paramsMap)))
    url = "%s/api/v1/user/getBalance" % APIURL
    return post(url, paramsStr)

def closePositions():
    placeOrder(symbol=coin.upper()+"-USDT", side="Ask",volume=amount , tradeType="Market", action="Close", price=0)
    placeOrder(symbol=coin.upper()+"-USDT", side="Bid",volume=amount , tradeType="Market", action="Close", price=0)
    return "close"

def placeOrder(symbol, side, price, volume, tradeType, action):
    paramsMap = {
        "symbol": symbol,
        "apiKey": APIKEY,
        "side": side,
        "entrustPrice": price,
        "entrustVolume": volume,
        "tradeType": tradeType,
        "action": action,
        "timestamp": int(time.time()*1000),
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/user/trade", "POST", paramsMap)))
    url = "%s/api/v1/user/trade" % APIURL
    return post(url, paramsStr)


mode = 0
price = 0
time.sleep(3)
okx = float(wd.title.split()[0])
bingx = float(wd2.find_element(by=By.XPATH, value='/html/body/div/section/div[2]/div[1]/div/div[2]/div/div[1]/div[3]/div/div[2]/div/div').text)
balance = float(str(getBalance()).split(',')[5].replace('"balance":', ''))
print("start !!!",okx , bingx, balance)

bey = 0.05

amount = balance*bey

while True:
    try:
        okx = float(wd.title.split()[0])
        bingx = float(wd2.find_element(by=By.XPATH, value='/html/body/div/section/div[2]/div[1]/div/div[2]/div/div[1]/div[3]/div/div[2]/div/div').text)
        if price != 0 and mode == 1 and okx > bingx:
            closePositions()
            mode = 0
            print("CLOSE  Balance = ", balance)
            balance = float(str(getBalance()).split(',')[5].replace('"balance":', ''))
            amount = balance*bey

        if price != 0 and mode == 2 and okx < bingx:
            closePositions()
            mode = 0
            print("CLOSE  Balance = ", balance)
            balance = float(str(getBalance()).split(',')[5].replace('"balance":', ''))
            amount = balance*bey

        if mode == 1 and bingx > price+0.15:
            closePositions()
            print("CLOSE  Balance = ", balance)
            balance = float(str(getBalance()).split(',')[5].replace('"balance":', ''))
            amount = balance*bey

        if mode == 2 and bingx < price-0.15:
            closePositions()
            print("CLOSE  Balance = ", balance)
            balance = float(str(getBalance()).split(',')[5].replace('"balance":', ''))
            amount = balance*bey

        if mode != 1 and okx < bingx-0.05:
            placeOrder(symbol=coin.upper()+"-USDT", side="Ask",volume=amount , tradeType="Market", action="Open", price=0)
            mode = 1
            price = bingx
            print("SELL", bingx)

        if mode != 2 and okx > bingx+0.05:
            placeOrder(symbol=coin.upper()+"-USDT", side="Bid",volume=amount , tradeType="Market", action="Open", price=0)
            mode = 2
            price = bingx
            print("BUY", bingx)
    except:
        try:
            closePositions()
        except:
            q = 0
