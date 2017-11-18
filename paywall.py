#!/usr/bin/python3

import cgi
import cgitb
import datetime
import json
import math
import os
import requests
import sys

from copy import copy
from datetime import datetime, timedelta, time
from random import randint
from bmdjson import check_address
from bmdjson import completed_quarter
from bmdjson import get_sha512_32_hash

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
WEB_DEBUG = "false"
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
# API Key (mydashdirect@gmail.com): cf3003ed342d
EXPLORER_RECEIVED_BY_URL = "https://chainz.cryptoid.info/dash/api.dws?q=multiaddr&n=0&key=cf3003ed342d&active="
EXPLORER_HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                   'AppleWebKit/537.36 (KHTML, like Gecko)'
                                   'Chrome/45.0.2454.101 Safari/537.36'),
                    'referer': 'https://explorer.dash.org/'}

COINMARKET_PRICE_URL = "https://api.coinmarketcap.com/v1/ticker/dash/?convert=USD"
COINMARKET_HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                   'AppleWebKit/537.36 (KHTML, like Gecko)'
                                   'Chrome/45.0.2454.101 Safari/537.36'),
                    'referer': 'https://coinmarketcap.com/'}

QR_URL = "https://chart.googleapis.com/chart?chs=120x120&cht=qr&chl="

#########

def hrs_until_midnight():
      tomorrow = datetime.today() + timedelta(1)
      midnight = datetime.combine(tomorrow, time())
      now = datetime.now()
      return (midnight - now).seconds / 60 / 60

def str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

def get_dash_price(debug):
      price = 0.0
      r = requests.get(COINMARKET_PRICE_URL,COINMARKET_HEADERS)
      if (r.status_code == requests.codes.ok):
            data = json.loads(r.text)
            if (debug): print(json.dumps(data, sort_keys=True, indent=8))
            price = float(str(data[0]["price_usd"]))
            if (debug): print("price = " + str(price))
      else:
            if (debug): print("Address check at " + COINMARKET_PRICE_URL + " status failed ["
                  + str(r.status_code) + "].  -> "
                  + str(r.raise_for_status()))
      return price

def get_dash_total_received(payee_keys,candidates,debug):
      big_url = EXPLORER_RECEIVED_BY_URL
      for key in payee_keys:
            payee = candidates[key]
            big_url = big_url + check_address(payee["address_signature"]) + "|"
      if (debug): print("big_url = " + str(big_url))
      r = requests.get(big_url,EXPLORER_HEADERS)
      if (r.status_code == requests.codes.ok):
            data = json.loads(r.text)
            for addrs in data["addresses"]:
                  key = get_sha512_32_hash(addrs["address"])
                  payee = candidates[key]
                  payee["total_received"] = float(str(addrs["total_received"] * .00000001))
                  if (debug): print("\nAfter Total Received " + str(addrs["total_received"]) + " added : " + json.dumps(payee, sort_keys=True, indent=8))
            if (debug): print("candidates : " + json.dumps(candidates, sort_keys=True, indent=8))
      else:
            if (debug): print("Address check at " + big_url + "status failed ["
                  + str(r.status_code) + "].  -> "
                  + str(r.raise_for_status()))
      return candidates

def get_payee_keys(candidates,payment_count_current, payment_count_max,payment_deposit_limit,debug):
      payee_keys = []
      for record in candidates.keys():
            payee = candidates[record]
            if (debug): print("payee[address_signature] = " + str(payee["address_signature"]))
            if not payee["active"]:
                  continue

            address_balance = payee["address_balance"]
            if (address_balance == 0) :
                  address_balance = .00000001
            max_payment_todate = float(payment_count_current * payment_deposit_limit)
            max_address_deposit_limit = float(payment_count_max * payment_deposit_limit)
            
            if (debug) :
                  print("address_balance = " + str(address_balance))
                  print("payment_count_current * payment_deposit_limit = "
                        + str(float(payment_count_current)) + " * "
                        + str(float(payment_deposit_limit)))
                  print("max_payment_todate = " + str(max_payment_todate))
                  print("max_address_deposit_limit = " + str(max_address_deposit_limit))
                  print("address_balance >= max_address_deposit_limit = "
                        + str(address_balance >= max_address_deposit_limit))
                  print("address_balance >= max_payment_todate = "
                        + str(address_balance >= max_payment_todate))
            
            if (address_balance >= max_address_deposit_limit
                or address_balance >= max_payment_todate):
                  continue
            payee_keys.append(record)
            continue
      if (debug):
            print("candidates <in> " + str(len(candidates)) + "; payees <out> "
                  + str(len(payee_keys))
                  + " now_weekday = " + str(epoch_weekdays[now_weekday]))
      return (payee_keys)

def do_app_out(payee_out, settings, current_payment_deposit_limit):
      print("Content-Type: application/json\n")
      json_out = {}
      for payee in payee_out:
            payee["remaining_pmt_needed"] = round(current_payment_deposit_limit - payee["address_balance"],6)
            json_out[get_sha512_32_hash(payee["address"])]= (copy(payee))
            del payee["remaining_pmt_needed"]
      json_out["settings"] = settings
      print(str(json.dumps(json_out, indent=4, sort_keys=True)))
      
def do_wp_out(payee_out, settings, current_payment_deposit_limit):
      print("Content-Type: text/html\n")
      print("<html><head><title>Paywall Output</title></head><body>")

      if len(payee_out) > 0:
            for payee in payee_out:
                  print("<iframe src=" + QR_URL + str(payee["address_signature"]) + " frameborder=\"0\" scrolling=\"No\"></iframe>")
                  print("<small><i>" + str(payee["address_signature"]) + "</i></small><br>Dash Needed: "
                        + str(round(current_payment_deposit_limit - payee["address_balance"],6))
                        + "<br>Address presented is: " + ["Bad", "Valid"][True] + "</body></html>")
                  return  #only one
      else:
            print("<html><body>All these paywall needs have been filled."
                  + "<img src='https://i0.wp.com/donate.greencandle.io/DashDirect/wp-content/uploads/2017/10/heart-1-e1507301788504.png?resize=15%2C15&ssl=1'>"
                  + "<p> Click <a href=\"http://give.dashdirect.io\" target=\"_blank\" rel=\"noopener\">give.dashdirect.io</a>"
                  + " for other paywall locations. Have a wonderful day and come back soon! We appreciate you. </body></html>")

def do_text_out(payee_out, settings, current_payment_deposit_limit, PAYMENT_COUNT_CURRENT, PAYMENT_NEW_WEEK, COINMARKET_DASH_PRICE):
      print("Content-Type: text/plain\n")
      print()        
      print("----------  Updating balances of those still in need. --------------------")
      print()
      if len(payee_out) > 0:
            for payee in payee_out:
                  print(str(payee["address_signature"]) + " > needs "
                        + str(format(round(current_payment_deposit_limit - payee["address_balance"],4), '.4f'))
                        + " Dash to be full. -> Signature status = "
                        + ["Bad", "Valid"][True])
      else:
            print("All these paywall needs have been filled. Please check: "
                  + "http://give.dashdirect.io \nto view our other "
                  + "paywalls displaying other needs.  \n\nHave a wonderful day and come back "
                  + "soon! We appreciate you.")
      print()
      print("--------------------------------------------------------------------------")
      print()
      print("Notes:")
      print(" Addresses above are wait for payments in payment count ["+ str(PAYMENT_COUNT_CURRENT) + "]")
      print(" Today is [" + str(epoch_weekdays[now_weekday]) + "] the new week starts [" + str(PAYMENT_NEW_WEEK) + "]")
      print(" [" + str(round(hrs_until_midnight(),2)) + "] hours till next day [" + str(epoch_weekdays[now_weekday +1]) + "]")
      print(" Current Dash price in USD [" + str("%.2f" % COINMARKET_DASH_PRICE) + "]")
      print()
      print()
      print("Completed without error at : " + str(datetime.now()))
      print()

def paywall_output(json_directory, json_file, payment_count_max, payment_new_week,
                   payment_deposit_limit, payment_count_current, debug, testing):
      try:
            json_dir = json_directory
            addr_filename = json_file
            src_file = os.path.join(json_dir, addr_filename)
            
            debug = str2bool(debug)
            testing = str2bool(testing)
            
            form = cgi.FieldStorage()
            if (debug): print(str(form.getvalue("WP")))
            if (form.getvalue("WP") is None):
                  wp = False
            else:
                  wp = str2bool(form.getvalue("WP"))
                  
            if (debug): print(str(form.getvalue("APP")))
            if (form.getvalue("APP") is None):
                  app = False
            else:
                  app = str2bool(form.getvalue("APP"))

            if ((payment_new_week not in epoch_weekdays) and (payment_new_week.lower() != 'off')) :
                  sys.stderr.write("payment_new_week is invalid : " + payment_new_week + "!")
                  quit()

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
                  if (debug): print("Warning: loading 'settings' section from (" +  str(src_file)
                                    + ") JSON file.")
                  PAYMENT_COUNT_MAX = int(db["settings"][0]["payment_count_max"])
                  PAYMENT_NEW_WEEK = str(db["settings"][0]["payment_new_week"])
                  PAYMENT_DEPOSIT_LIMIT = float(db["settings"][0]["payment_deposit_limit"])
                  PAYMENT_COUNT_CURRENT = int(db["settings"][0]["payment_count_current"])
                  PAYMENT_IS_NEW_WEEK = str2bool(str(db["settings"][0]["payment_is_new_week"]))
                  DEBUG = str2bool(str(db["settings"][0]["debug"]))
            else:
                  if (debug): print("Warning: 'settings' section not found in JSON file; "
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
            
      except:
            sys.stderr.write("Bad file format!")
            quit()

      #########
      # process addresses here: only get payees who still need funds to check http balance
      #########
      COINMARKET_DASH_PRICE = get_dash_price(debug)
      check_all_candidates = False
      if (debug): print("PAYMENT_IS_NEW_WEEK = " + str(PAYMENT_IS_NEW_WEEK))
      if (debug): print("PAYMENT_NEW_WEEK = " + str(PAYMENT_NEW_WEEK))
      if (debug): print("epoch_weekdays[now_weekday] = " + str(epoch_weekdays[now_weekday]))
      if (debug): print("PAYMENT_COUNT_CURRENT) + 1 = " + str(int(PAYMENT_COUNT_CURRENT) + 1))
      if (debug): print("PAYMENT_COUNT_MAX = " + str(int(PAYMENT_COUNT_MAX)))

      if (debug): print("PAYMENT_NEW_WEEK.lower() == off = " + str(PAYMENT_NEW_WEEK.lower() == "off"))
      if (debug): print("not PAYMENT_IS_NEW_WEEK = " + str(not PAYMENT_IS_NEW_WEEK))
      if (debug): print("epoch_weekdays[now_weekday] == PAYMENT_NEW_WEEK = " + str(epoch_weekdays[now_weekday] == PAYMENT_NEW_WEEK))
      if (debug): print("(int(PAYMENT_COUNT_CURRENT) + 1) <= int(PAYMENT_COUNT_MAX) = " + str((int(PAYMENT_COUNT_CURRENT) + 1) <= int(PAYMENT_COUNT_MAX)))
                  
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
            if (debug): print("Everyone is ready for next payment (#" + str(PAYMENT_COUNT_CURRENT) + ") \n\n")
            payee_keys = candidates.keys()
      else:
            payee_keys = get_payee_keys(candidates,PAYMENT_COUNT_CURRENT,
                                        PAYMENT_COUNT_MAX,
                                        PAYMENT_DEPOSIT_LIMIT, debug)

      payee_out = []
      current_payment_deposit_limit = PAYMENT_DEPOSIT_LIMIT * PAYMENT_COUNT_CURRENT
      if (debug) :
            print("PAYMENT_COUNT_CURRENT (before) = " + str(PAYMENT_COUNT_CURRENT))
            print("current_payment_deposit_limit (after) = " + str(current_payment_deposit_limit))
      if (PAYMENT_COUNT_CURRENT <= PAYMENT_COUNT_MAX and len(payee_keys) > 0) :
            if (debug):
                  print("PAYMENT_COUNT_CURRENT > PAYMENT_COUNT_MAX (" + str(PAYMENT_COUNT_CURRENT) + " > " + str(PAYMENT_COUNT_MAX) + ")")
                  print("PAYMENT_COUNT_CURRENT " + str(PAYMENT_COUNT_CURRENT))
            candidates = get_dash_total_received(payee_keys,db["pay_to"],debug)
            for payee in candidates.values():
                  if (debug): print("payee : " + json.dumps(payee, sort_keys=True, indent=8))
                  if (payee["active"]):
                        payee.setdefault("total_received", 0.0)
                        address_balance = float(payee["total_received"])
                        if (address_balance > payee["address_balance"]):
                              # add new delta transactions to the json file
                              if (debug): print("\naddress_balance (" + str(address_balance) + ") > payee[address_balance] (" + str(payee["address_balance"]) + ")")
                              yr,qtr = completed_quarter(datetime.today())
                              new_payment = {}
                              new_payment = {
                                    "amount" : round(address_balance - payee['address_balance'],6),
                                    "dash_price" : COINMARKET_DASH_PRICE,
                                    "completed_quarter" : str(yr) + "-" + str(qtr),
                                    "ts_created" : int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
                              }
                              payee["payments"].append(new_payment)
                              payee["address_balance"] = address_balance

                              if (debug) : 
                                    print("\nAfter payments added: "+  json.dumps(payee, sort_keys=True, indent=8))
                        if (payee["address_balance"] <= current_payment_deposit_limit):
                              payee_out.append(payee)
            if (PAYMENT_COUNT_CURRENT >= PAYMENT_COUNT_MAX) :
                  PAYMENT_COUNT_CURRENT = PAYMENT_COUNT_MAX

            db["pay_to"] = candidates
            db['settings'] = [{'_comment':"payment_new_week options: ['Sun','Mon','Tue','Wed','Thu','Fri','Sat','OFF']",
                               'payment_count_max':PAYMENT_COUNT_MAX,
                               'payment_new_week':PAYMENT_NEW_WEEK,
                               'payment_deposit_limit':PAYMENT_DEPOSIT_LIMIT,
                               'payment_count_current':PAYMENT_COUNT_CURRENT,
                               'payment_is_new_week': PAYMENT_IS_NEW_WEEK,
                               "debug": debug
            }]
            if (debug) : print("\ndb : "+  json.dumps(db, sort_keys=True, indent=8))

      #########
      # write changes back down
      #########
      with open(src_file, 'w') as outfile:
            json.dump(db, outfile, indent=2, sort_keys=True)

      if (app):            
            do_app_out(payee_out, db['settings'], current_payment_deposit_limit)
      elif (wp):
            do_wp_out(payee_out, db['settings'], current_payment_deposit_limit)
      else:
            do_text_out(payee_out, db['settings'], current_payment_deposit_limit,PAYMENT_COUNT_CURRENT, PAYMENT_NEW_WEEK, COINMARKET_DASH_PRICE)
            if (debug) :
                  print("FILE                       - " + src_file)
                  print("EXPLORER_RECEIVED_BY_URL   - " + EXPLORER_RECEIVED_BY_URL)
                  print("PAYMENT_COUNT_MAX          - " + str(PAYMENT_COUNT_MAX))
                  print("PAYMENT_NEW_WEEK           - " + str(PAYMENT_NEW_WEEK))
                  print("PAYMENT_DEPOSIT_LIMIT      - " + str(PAYMENT_DEPOSIT_LIMIT))
                  print("PAYMENT_COUNT_CURRENT      - " + str(PAYMENT_COUNT_CURRENT))
                  print("PAYMENT_IS_NEW_WEEK        - " + str(PAYMENT_IS_NEW_WEEK))
            
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
