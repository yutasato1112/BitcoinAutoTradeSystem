#初期設定
# -*- coding: utf-8 -*-
from ast import While
import bitbank_api_key
from utils.notify import send_line_notify
import python_bitbankcc
import requests
import pandas as pd
import time
from datetime import datetime
import warnings
warnings.simplefilter('ignore',FutureWarning)
f=open('Auto_Trade_Status','w')
"""メモ
buy_Yen:指値購入する際の日本円
buy_BTC:指値購入する際のBTC量
sell_Yen:指値売却する際の日本円
sell_BTC:指値売却する際のBTC量
"""

#初期BTC購入金額入力
buyTimeValue=input("初期BTC購入金額の入力:")

#情報取得
Base_URL = "https://public.bitbank.cc"
def checkValue():
    url = Base_URL+"/btc_jpy/ticker"
    r=requests.get(url,timeout=5)
    r=r.json()
    last=r['data']['last']
    return last

def amountJPY():
    assets=bitbank_api_key.private.get_asset()
    asset_JPY=assets['assets'][0]['onhand_amount']
    return asset_JPY

def amountBTC():
    assets=bitbank_api_key.private.get_asset()
    asset_BTC=assets['assets'][1]['onhand_amount']
    return asset_BTC

#Bitcoin指値購入
def Bitcoin_Limit_Buy(buy_BTC,amount):
    bitbank_api_key.private.order('btc_jpy',buy_BTC,amount,'buy','limit')
    send_line_notify('BTC購入処理を正常に終了しました')
    print('BTC購入処理を正常に終了しました')
    f.write('BTC購入処理を正常に終了しました')
    f.write('\n')

#Bitcoin指値売却
def Bitcoin_Limit_Sell(sell_BTC,amount):
    bitbank_api_key.private.order('btc_jpy',sell_BTC,amount,'sell','limit')
    send_line_notify('BTC売却処理を正常に終了しました')
    print('BTC売却処理を正常に終了しました')
    f.write('BTC売却処理を正常に終了しました')
    f.write('\n')

AllAsset=float(amountJPY())+float(amountBTC())*float(checkValue())
commission=float(AllAsset)*float(0.0012)

#運用main
interval=60*15
duration=20
nl=0
df=pd.DataFrame()
send_line_notify('自動取引を開始しました')
f.write('自動取引を開始しました')
f.write('\n')
print('now loading...', nl , '/' , duration)
f.write('now loading...')
f.write(str(nl))
f.write('/')
f.write(str(duration))
f.write('\n')
while True:
    f=open('Auto_Trade_Status','a')
    time.sleep(interval)
    df=df.append({'price':checkValue()}, ignore_index=True)

    if len(df)<duration:
        nl+=1
        print('now loading...', nl , '/' , duration)
        f.write('now loading...')
        f.write(str(nl))
        f.write('/')
        f.write(str(duration))
        f.write('\n')
        continue

    #ボリンジャーバンドの計算
    df['SMA']=df['price'].rolling(window=duration).mean()
    df['std']=df['price'].rolling(window=duration).std()

    df['-2sigma']=df['SMA']-2*df['std']
    df['2sigma']=df['SMA']+2*df['std']

    print(df)
    f.write(str(df))
    f.write('\n')

    AllAsset=float(amountJPY())+float(amountBTC())*float(checkValue())
    commission=float(checkValue())*float(0.0015)

    #注文条件
    if df['price'].iloc[-1] < str(df['-2sigma'].iloc[-1]):
        if float(amountJPY())>float(5000):
            print("buy")
            buyTimeValue=checkValue()
            print(buyTimeValue)
            send_line_notify('買い')
            f.write('買い')
            f.write(str(buyTimeValue))
            f.write('\n')
            BTCValue=float(checkValue())+5
            Bitcoin_Limit_Buy(float(checkValue())+5, float(amountJPY())/float(BTCValue))

    if str(df['2sigma'].iloc[-1]) < df['price'].iloc[-1]:
        if float(amountJPY()) < 5000:
            if float(buyTimeValue)+float(commission) < float(checkValue()):
                print("sell")
                print(checkValue())
                send_line_notify('売り')
                f.write('売り')
                f.write(str(checkValue()))
                f.write('\n')
                Bitcoin_Limit_Sell(float(checkValue())-5, amountBTC())
    f.close()