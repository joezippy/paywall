#!/usr/bin/python3

import cgi
import cgitb
import datetime
import json
import math
import os
import requests
import sys

from datetime import datetime, timedelta, time
from random import randint
from bmdjson import check_address

############################################################################
# File: paywall.py
# Repository: https://github.com/joezippy/paywall
# Requirements: Python 3.5, webserver and CGI
#
# The paywall.py file was create to help with dash tipping and allow wallet
# automation regarding "top-ups" which could be use in a varity of ways in
# the community to pay it forward.
#
# You can find the creator of this tool in the dash slack my the name of
# joezippy Additional documentation and this file can be found in the
# repository
#
# Enjoy!
############################################################################

#########
# They are default WEB values if 'settings' can't be found in json file
WEB_JSON_DIR = "."
WEB_JSON_FILE = "default.json"
WEB_PAYMENT_COUNT_MAX = 104
WEB_PAYMENT_NEXT_WEEK = "Sun" 
WEB_PAYMENT_DEPOSIT_LIMIT = 0.14  # 40÷284.31 usd
WEB_PAYMENT_COUNT_CURRENT = 0
WEB_PAYMENT_IS_NEW_WEEK = "no"
WEB_DEBUG = "no"
WEB_TESTING = "no"

#########
# This defines the max_pmt_freq in sec
# The datetime.utcfromtimestamp(0) function returns the number of seconds since the epoch as
# seconds in UTC.  # https://www.epochconverter.com/
# 60 s / min
# 3600 s / hr
# 86400 s / day
# s means second
#
# Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
now_weekday = datetime.today().weekday()
epoch_weekdays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun','Mon']
    
#########
# This defines the blockchain explorer that will be use to fetch the balance by the address.
# Funds have to be moved by the address owner, if you expect subsiquent deposits based on pmt_freq_ms

# the JSON file address will be concatinated on the end
EXPLORER_RECEIVED_BY_URL = "https://explorer.dash.org/chain/Dash/q/getreceivedbyaddress/"
EXPLORER_CHECK_ADDRESS_URL = "https://explorer.dash.org/chain/Dash/q/checkaddress/"
EXPLORER_CHECK_ADDRESS_ERR_CODES = ['X5', 'SZ', 'CK']
EXPLORER_HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                   'AppleWebKit/537.36 (KHTML, like Gecko)'
                                   'Chrome/45.0.2454.101 Safari/537.36'),
                    'referer': 'https://explorer.dash.org/'}

COINMARKET_PRICE_URL = "https://api.coinmarketcap.com/v1/ticker/dash/?convert=USD"
COINMARKET_HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                   'AppleWebKit/537.36 (KHTML, like Gecko)'
                                   'Chrome/45.0.2454.101 Safari/537.36'),
                    'referer': 'https://coinmarketcap.com/'}
#########

def hrs_until_midnight():
      tomorrow = datetime.today() + timedelta(1)
      midnight = datetime.combine(tomorrow, time())
      now = datetime.now()
      return (midnight - now).seconds / 60 / 60

def str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

def getDashPrice(debug):
      price = 0.0
      r = requests.get(COINMARKET_PRICE_URL,COINMARKET_HEADERS)
      if (r.status_code == requests.codes.ok):
            data = json.loads(r.text)
            if (debug): print(json.dumps(data, sort_keys=True, indent=8))
            price = float(str(data[0]["price_usd"]))
            if (debug): print("price = " + str(price))
      return price


def get_payee_keys(candidates,payment_count_current, payment_count_max,payment_deposit_limit,debug):
      payee_keys = []
      for record in candidates.keys():
            payee = candidates[record]
            if not payee["active"]:
                  continue

            address_balance = payee["address_balance"]
            if (debug): print("address_balance = " + str(address_balance))
            
            if (address_balance == 0) :
                  address_balance = .00000001

            if (debug) : print("payment_count_current * payment_deposit_limit = "
                  + str(float(payment_count_current)) + " * "
                  +  str(float(payment_deposit_limit)))
            max_payment_todate = float(payment_count_current * payment_deposit_limit)
            if (debug): print("max_payment_todate = " + str(max_payment_todate))
            
            max_address_deposit_limit = float(payment_count_max * payment_deposit_limit)
            
            if (debug): print("max_address_deposit_limit = " + str(max_address_deposit_limit))
            
            if (debug): print("address_balance >= max_address_deposit_limit = "
                              + str(address_balance >= max_address_deposit_limit))
            if (debug): print("address_balance >= max_payment_todate = "
                              + str(address_balance >= max_payment_todate))
            
            if (address_balance >= max_address_deposit_limit
                or address_balance >= max_payment_todate):
                  continue
            payee_keys.append(record)
            continue
      if (debug): print("candidates <in> " + str(len(candidates)) + "; payees <out> "
                        + str(len(payee_keys))
                        + " now_weekday = " + str(epoch_weekdays[now_weekday]))
      return (payee_keys)

def paywall_output(json_directory, json_file, payment_count_max, payment_new_week,
                   payment_deposit_limit, payment_count_current, debug, testing):
      
      print("Content-Type: text/plain\n")

      if ((payment_new_week not in epoch_weekdays) and (payment_new_week.lower() != 'off')) :
            print ("\n\npayment_new_week is invalid : " + payment_new_week + "\n\n")
            return
      
      json_dir = json_directory
      addr_filename = json_file
      src_file = os.path.join(json_dir, addr_filename)
      
      debug = str2bool(debug)
      testing = str2bool(testing)
      
      sys.stdout.flush()
      
      #########
      # read source
      #########
      db = None
      with open(src_file) as data_file:    
            db = json.load(data_file)
            
      if db is None:
            sys.stderr.write("Bad file format!")
            quit()
            
      # This is to handle cases where no settings are found in a new file
      if len(db["settings"]) > 0:
            if (debug): print("\nWarning: loading 'settings' section from (" +  str(src_file)
                              + ") JSON file.")
            PAYMENT_COUNT_MAX = int(db["settings"][0]["payment_count_max"])
            PAYMENT_NEW_WEEK = str(db["settings"][0]["payment_new_week"])
            PAYMENT_DEPOSIT_LIMIT = float(db["settings"][0]["payment_deposit_limit"])
            PAYMENT_COUNT_CURRENT = int(db["settings"][0]["payment_count_current"])
            PAYMENT_IS_NEW_WEEK = str2bool(str(db["settings"][0]["payment_is_new_week"]))
            DEBUG = str2bool(str(db["settings"][0]["debug"]))
      else:
            if (debug): print("\nWarning: 'settings' section not found in JSON file; "
                              + "running with paywall default values found below.\n")
            PAYMENT_COUNT_MAX = WEB_PAYMENT_COUNT_MAX
            PAYMENT_NEW_WEEK = str(WEB_PAYMENT_NEXT_WEEK)
            PAYMENT_DEPOSIT_LIMIT = WEB_PAYMENT_DEPOSIT_LIMIT
            PAYMENT_COUNT_CURRENT = WEB_PAYMENT_COUNT_CURRENT
            PAYMENT_IS_NEW_WEEK = str2bool(str(WEB_PAYMENT_IS_NEW_WEEK))
            DEBUG = str2bool(str(WEB_DEBUG))
            
      #########
      # this is for staging testing parms
      #########
      if (testing) :
            if (debug) : print("Warning: overloading source data w/ testing data.")
            PAYMENT_COUNT_MAX = int(payment_count_max)
            PAYMENT_NEW_WEEK = str(payment_new_week)
            PAYMENT_DEPOSIT_LIMIT = float(payment_deposit_limit)
            PAYMENT_COUNT_CURRENT = int(payment_count_current)
            
      print()        
      print("----------  Updating balanced of those still in need. --------------------")
      print()
      sys.stdout.flush()
      
      #########
      # process addresses here: only get payees who still need funds to check http balance
      #########
      COINMARKET_DASH_PRICE = getDashPrice(debug)
      check_all_candidates = False
      if (debug): print("PAYMENT_IS_NEW_WEEK = " + str(PAYMENT_IS_NEW_WEEK))
      if (debug): print("PAYMENT_NEW_WEEK = " + str(PAYMENT_NEW_WEEK))
      if (debug): print("epoch_weekdays[now_weekday] = " + str(epoch_weekdays[now_weekday]))
      if (debug): print("PAYMENT_COUNT_CURRENT) + 1 = " + str(int(PAYMENT_COUNT_CURRENT) + 1))
      if (debug): print("PAYMENT_COUNT_MAX = " + str(int(PAYMENT_COUNT_MAX)))

      if (debug): print("T1 = " + str(PAYMENT_NEW_WEEK.lower() == "off"))
      if (debug): print("T2 = " + str(not PAYMENT_IS_NEW_WEEK))
      if (debug): print("T3 = " + str(epoch_weekdays[now_weekday] == PAYMENT_NEW_WEEK))
      if (debug): print("T4 = " + str((int(PAYMENT_COUNT_CURRENT) + 1) <= int(PAYMENT_COUNT_MAX)))
                  
      if (PAYMENT_NEW_WEEK.lower() == "off") :
            PAYMENT_COUNT_MAX = 1
            PAYMENT_COUNT_CURRENT = 1
            PAYMENT_IS_NEW_WEEK = False            
      else : 
            if (not PAYMENT_IS_NEW_WEEK and epoch_weekdays[now_weekday] == PAYMENT_NEW_WEEK  
                      and (int(PAYMENT_COUNT_CURRENT) + 1) <= int(PAYMENT_COUNT_MAX)) :
                  PAYMENT_COUNT_CURRENT = PAYMENT_COUNT_CURRENT + 1
                  PAYMENT_IS_NEW_WEEK = True
                  check_all_candidates = True
            if (epoch_weekdays[now_weekday] != PAYMENT_NEW_WEEK) :
                  PAYMENT_IS_NEW_WEEK = False

      candidates = db["pay_to"]
      if (check_all_candidates) :
            print("Everyone is ready for next payment (#"
                  + str(PAYMENT_COUNT_CURRENT) + ") \n\n")
            payee_keys = candidates.keys()
      else:
            payee_keys = get_payee_keys(candidates,PAYMENT_COUNT_CURRENT,
                                        PAYMENT_COUNT_MAX,
                                        PAYMENT_DEPOSIT_LIMIT, debug)

      if (PAYMENT_COUNT_CURRENT <= PAYMENT_COUNT_MAX and len(payee_keys) > 0) :
            if (debug) : print("PAYMENT_COUNT_CURRENT > PAYMENT_COUNT_MAX (" + str(PAYMENT_COUNT_CURRENT) + " > " + str(PAYMENT_COUNT_MAX) + ")")
            if (debug) : print("PAYMENT_COUNT_CURRENT " + str(PAYMENT_COUNT_CURRENT))
            candidates = db["pay_to"]
            for key in payee_keys:
                  payee = candidates[key]
                  if (debug) : print("\nBefore payments added : " + json.dumps(payee, sort_keys=True, indent=8))
                  payee_res = check_address(payee["address_signature"])
                  if (payee_res["sig_good"] and payee["active"] is True):
                        url = EXPLORER_RECEIVED_BY_URL + str(payee_res["sig_addr"])
                        if (debug) : print("\nurl = " + url)
                        r = requests.get(url,EXPLORER_HEADERS)
                        if (r.status_code == requests.codes.ok):
                              address_balance = float(r.text)
                              if (address_balance > payee["address_balance"]):
                                    # add new delta transactions to the json file
                                    if (debug) : print("address_balance (" + str(address_balance) + ") > payee[address_balance] (" + str(payee["address_balance"]) + ")")

                                    new_payment = {}
                                    new_payment = {
                                          "amount" : round(address_balance - payee['address_balance'],6),
                                          "dash_price" : COINMARKET_DASH_PRICE,
                                          "ts_created" : int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
                                    }
                                    payee["payments"].append(new_payment)
                                    payee["address_balance"] = address_balance
                  if (debug) : print("\nAfter payments added: "+  json.dumps(payee, sort_keys=True, indent=8))
                  if (debug) : print("PAYMENT_COUNT_CURRENT (before) = " + str(PAYMENT_COUNT_CURRENT))
                  current_payment_deposit_limit = PAYMENT_DEPOSIT_LIMIT * PAYMENT_COUNT_CURRENT
                  if (debug) : print("current_payment_deposit_limit (after) = " + str(current_payment_deposit_limit))
                  
                  if (payee["address_balance"] <= current_payment_deposit_limit):
                        print(str(payee_res["sig_addr"]) + " > needs "
                              + str(round(current_payment_deposit_limit - payee["address_balance"],6))
                              + " Dash to be full. -> Signature status = "
                              + ["Bad", "Valid"][payee_res["sig_good"]])
                  else:
                        print("Dash blockchain explorer address check status failed ["
                              + str(r.status_code) + "].  -> "
                              + str(r.raise_for_status()))
      else:
            print("All these paywall needs have been filled. Please check here: \n"
                  + "https://donate.greencandle.io/DashDirect/index.php/paywalls/ \nto view our other "
                  + "paywalls displaying other neededs.  \n\nHave a wonderful day and come back "
                  + "soon! We appreciate you.")
      print()
      print("--------------------------------------------------------------------------")
      print()
      print("Notes:")
      print(" Addresses above are wait for payments in payment count ["
            + str(PAYMENT_COUNT_CURRENT) + "]")
      print(" Today is [" + str(epoch_weekdays[now_weekday]) + "] the new week starts ["
            + str(PAYMENT_NEW_WEEK) + "]")
      print(" [" + str(round(hrs_until_midnight(),2)) + "] hours till next day ["
            + str(epoch_weekdays[now_weekday +1]) + "]")
      print(" Current Dash price in USD [" + str("%.2f" % COINMARKET_DASH_PRICE) + "]")
      print()
      print()
      print("Completed without error at : " + str(datetime.now()))
      print()
      
      if (debug) :
            print("FILE                       - " + src_file)
            print("EXPLORER_RECEIVED_BY_URL   - " + EXPLORER_RECEIVED_BY_URL)
            print("EXPLORER_CHECK_ADDRESS_URL - " + EXPLORER_CHECK_ADDRESS_URL)
            print("PAYMENT_COUNT_MAX          - " + str(PAYMENT_COUNT_MAX))
            print("PAYMENT_NEW_WEEK           - " + str(PAYMENT_NEW_WEEK))
            print("PAYMENT_DEPOSIT_LIMIT      - " + str(PAYMENT_DEPOSIT_LIMIT))
            print("PAYMENT_COUNT_CURRENT      - " + str(PAYMENT_COUNT_CURRENT))
            print("PAYMENT_IS_NEW_WEEK        - " + str(PAYMENT_IS_NEW_WEEK))

      if (PAYMENT_COUNT_CURRENT >= PAYMENT_COUNT_MAX) :
            PAYMENT_COUNT_CURRENT = PAYMENT_COUNT_MAX


      db['settings'] = [{'_comment':"payment_new_week options: ['Sun','Mon','Tue','Wed','Thu','Fri','Sat','OFF']",
                         'payment_count_max':PAYMENT_COUNT_MAX,
                         'payment_new_week':PAYMENT_NEW_WEEK,
                         'payment_deposit_limit':PAYMENT_DEPOSIT_LIMIT,
                         'payment_count_current':PAYMENT_COUNT_CURRENT,
                         'payment_is_new_week': PAYMENT_IS_NEW_WEEK,
                         "debug": debug
      }]

      #########
      # write changes back down
      #########
      if (testing) :
            with open(src_file + ".out", 'w') as outfile:
                  json.dump(db, outfile, indent=2, sort_keys=True)
      else :
            with open(src_file, 'w') as outfile:
                  json.dump(db, outfile, indent=2, sort_keys=True)
                  
if __name__ == "__main__":
      # def paywall_output(json_directory, json_file, payment_count_max, payment_new_week,
      #               payment_deposit_limit, payment_count_current, debug, testing):
      try:
            if(len(sys.argv) == 9):
                  paywall_output(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],
                                 sys.argv[6],sys.argv[7],sys.argv[8])
            else:
                  paywall_output(WEB_JSON_DIR,WEB_JSON_FILE, WEB_PAYMENT_COUNT_MAX,
                                 WEB_PAYMENT_NEXT_WEEK, WEB_PAYMENT_DEPOSIT_LIMIT,
                                 WEB_PAYMENT_COUNT_CURRENT, WEB_DEBUG,
                                 WEB_TESTING)
                  
      except Exception as e:
            print("Exception: ",e)
            raise
