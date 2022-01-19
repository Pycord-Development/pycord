import requests
from requests import Request, Session
#Coinmarketcap call
coinurl = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
coinparameters = {
  'symbol':'WOOL',
  'convert':'USD'
}
coinheaders = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': config['coinmarketcapapi'],
}
session = Session()
session.headers.update(coinheaders)
try:
  response = session.get(coinurl, params=coinparameters).json()
  data = response['data']
  ethdata=data['WOOL']
  pricedata=ethdata['quote']
  usdprice=pricedata['USD']
  ethprice=usdprice['price']
  print(usdprice['price'])
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)
  