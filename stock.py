#!/usr/bin/env python3

import datetime, pytz, holidays
import yfinance as yf
import pandas as pd
import configparser
import sys
import signal

tz = pytz.timezone('US/Eastern')
us_holidays = holidays.US()

def signal_handler(signum, frame):
    raise Exception("Timed out!")

signal.signal(signal.SIGALRM, signal_handler)
signal.alarm(20)   # Ten seconds

def afterHours(now = None):
  if not now:
      now = datetime.datetime.now(tz)
  openTime = datetime.time(hour = 9, minute = 30, second = 0)
  closeTime = datetime.time(hour = 16, minute = 0, second = 0)
  # If a holiday
  if now.strftime('%Y-%m-%d') in us_holidays:
      return True
  # If before 0930 or after 1600
  if (now.time() < openTime) or (now.time() > closeTime):
      return True
  # If it's a weekend
  if now.date().weekday() > 4:
      return True

  return False

config = configparser.ConfigParser()

# File must be opened with utf-8 explicitly
with open('/home/mredlars/.config/polybar/stock-config', 'r', encoding='utf-8') as f:
  config.read_file(f)

# Everything except the general section
stocks = [x for x in config.sections() if x != 'general']

# stockslist = ' '.join(stocks)
# history = yf.download(tickers=stockslist, period="5d", interval="1h", group_by="ticker", prepost=True, progress=False)
# ticker = Ticker(tickers=stockslist)
try:
  for stock in stocks:
    icon = config[stock]['icon']
    ticker = yf.Ticker(stock)
    quote = ticker.info

    if afterHours():
      period="5d"
      prepost=True
    else:
      period="1d"
      prepost=False

    history = yf.download(tickers=stock, period=period, interval="1m", prepost=prepost, progress=False)
    price = history.loc[:,'Close'][-1]
    change = round((1-quote['regularMarketPreviousClose']/price)*100, 2)

    if change > 0:
      arrow = config['general']['iconup']
      if afterHours():
        color = '%{F#009d00}'
      else:
        color = '%{F#0f0}'
    else:
      arrow = config['general']['icondown']
      if afterHours():
        color = '%{F#9d0000}'
      else:
        color = '%{F#f00}'

    ecolor = '%{F-}'

    display_opt = config['general']['display']
    if display_opt == 'both' or display_opt == None:
      sys.stdout.write(f'{icon} {color} {arrow} {price:.2f}/{change:+}%  {ecolor}')
    elif display_opt == 'percentage':
      sys.stdout.write(f'{icon} {color} {arrow} {change:+}%  {ecolor}')
    elif display_opt == 'price':
      sys.stdout.write(f'{icon} {color} {arrow} {price:.2f}  {ecolor}')
except Exception:
    print("Timed out!")
