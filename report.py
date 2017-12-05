#!/usr/bin/python3

import cgi
import cgitb
import datetime
import json
import math
import os
import requests
import sys

from os.path import dirname, abspath
from datetime import datetime, timedelta, time
from random import randint
from bmdjson import get_dash_price, get_dash_chain_totals

############################################################################
# File: report.py
# Repository: https://github.com/joezippy/paywall
# Requirements: Python 3.5, webserver and CGI
#
# The report.py file was create to generate reports from paywall.py json files
#
# You can find the creator of this tool in the dash discord my the name of
# joezippy Additional documentation and this file can be found in the
# repository
#
# Enjoy!
############################################################################

#########
# They are default WEB values if 'settings' can't be found in json file
WEB_JSON_DIR = "."
WEB_JSON_FILE = "default.json"
WEB_DEBUG = "no"

EXPLORER_RECEIVED_BY_URL = "https://chainz.cryptoid.info/dash/api.dws?q=multiaddr&n=0&key=cf3003ed342d&active="
EXPLORER_HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                   'AppleWebKit/537.36 (KHTML, like Gecko)'
                                   'Chrome/45.0.2454.101 Safari/537.36'),
                    'referer': 'https://explorer.dash.org/'}

#########

def str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

def do_wp_output(candidates,debug):
      PAYWALL_TOTAL_DASH = 0.0      
      PAYWALL_TOTAL_US = 0.0
      data_out = {}
      payee_keys = candidates.keys()
      for key in payee_keys:
            payee = candidates[key]
            # loop and calc all paywment here
            address_total_dash = 0.0
            address_total_us = 0.0
            for pay in payee["payments"] :
                  if (debug): print(str(pay["amount"]) + " * "
                                    + str(pay["dash_price"])
                                    + " Dash => "
                                    + str(pay["amount"]*pay["dash_price"]) + " USD")
                  address_total_dash = address_total_dash + pay["amount"]
                  address_total_us = address_total_us + pay["amount"]*pay["dash_price"]
            PAYWALL_TOTAL_DASH = PAYWALL_TOTAL_DASH + address_total_dash
            PAYWALL_TOTAL_US = PAYWALL_TOTAL_US + address_total_us
            data_out[payee["address"]] = ["Dash : " + str(format(round(address_total_dash,4), '.4f')) ,
                                          "USD : " + str(format(round(address_total_us,2), '.2f'))]

      print("Content-Type: text/html\n\n")
      print("<html><body><title>Paywall Report</title><small><a href=\"")
      print("https://" + str(os.environ["HTTP_HOST"]) + str(os.environ["SCRIPT_NAME"]))
      print("\" target=\"_blank\" rel=\"noopener\">Current Paywall Totals</a>: <br>"
            + str(round(PAYWALL_TOTAL_DASH,3)) + " Dash; "
            + str(round(PAYWALL_TOTAL_US,2)) + " USD </small></body></html>") 
      return

def do_qtr_output(candidates,completed_quarter,completed_quarter_curr,src_file,debug):
      PAYWALL_TOTAL_DASH = 0.0      
      PAYWALL_TOTAL_US = 0.0
      data_out = {}
      payee_keys = candidates.keys()
      for key in payee_keys:
            payee = candidates[key]
            # loop and calc all paywment here
            for pay in payee["payments"] :
                  if (debug) : print(str(payee["address"]) + " -> " + str(pay["completed_quarter"])
                        + " -> (" + str(pay["amount"]) + " * " + str(pay["dash_price"]) + ") Dash => " + str(pay["amount"]*pay["dash_price"]) + " USD")
                  PAYWALL_TOTAL_DASH = PAYWALL_TOTAL_DASH + pay["amount"]
                  PAYWALL_TOTAL_US = PAYWALL_TOTAL_US + pay["amount"]*pay["dash_price"]
                  if (pay["completed_quarter"] in data_out) :
                        qtr_dash = float(data_out[pay["completed_quarter"]]["Dash"])
                        qtr_us = float(data_out[pay["completed_quarter"]]["USD"])
                        data_out[pay["completed_quarter"]] = {"Dash" : str(format(round(pay["amount"]+qtr_dash,4), '.4f')) ,
                                                              "USD" : str(format(round((pay["amount"]*pay["dash_price"])+qtr_us,2), '.2f'))}
                  else:
                        #first find of qtr
                        data_out[pay["completed_quarter"]] = {"Dash" : str(format(round(pay["amount"],4), '.4f')) ,
                                                              "USD" : str(format(round(pay["amount"]*pay["dash_price"],2), '.2f'))}

      if (len(completed_quarter) > 0 and len(completed_quarter_curr) > 0) :
            simple_out = "0"
            if (completed_quarter in data_out):
                  if (completed_quarter_curr.lower() in ("usd", "us")):
                        simple_out = str(data_out[completed_quarter]["USD"])                        
                  else:
                        simple_out = str(data_out[completed_quarter]["Dash"])
            print("Content-Type: text/plain\n")
            print(simple_out)
      else:
            print("Content-Type: text/html\n\n")
            print("<html><head><title>Paywall Report</title><body><h3>Paywall Address Report (" + completed_quarter + ")</h3>")
            print("<pre>")
            print("---------------")      
            for key in sorted(data_out):
                  print(str(key) + " - " + str(data_out[key]))
            print("---------------")
            print("Notes:")
            print("  UDS value is calculated based on the deposit capture price, not the current Dash price.")
            print()
            print("FILE                      - " + dirname(abspath(__file__)) + "/" + src_file)
            print("PAYWALL_TOTAL_DASH        - " + str(format(round(PAYWALL_TOTAL_DASH,4), '.4f')))
            print("PAYWALL_TOTAL_US          - " + str(format(round(PAYWALL_TOTAL_US,2), '.2f')))
            print()
            print("Completed without error at : " + str(datetime.now()))
            print()
            print("</pre></body></html>")
      return

def do_html_output(candidates,src_file,details,debug):
      COINMARKET_DASH_PRICE = get_dash_price(debug)
      CHAIN_RECEIVED_TOTAL_DASH = 0.0      
      CHAIN_RECEIVED_TOTAL_US = 0.0
      CHAIN_SENT_TOTAL_DASH = 0.0      
      CHAIN_SENT_TOTAL_US = 0.0
      PAYWALL_DEPOSIT_TOTAL_DASH = 0.0      
      PAYWALL_DEPOSIT_TOTAL_US = 0.0
      data_out = {}
      payee_keys = candidates.keys()
      for key in payee_keys:
            payee = candidates[key]

            address_received_total_dash = float(payee["total_received"])
            address_received_total_us = float(payee["total_received"]) * COINMARKET_DASH_PRICE
            CHAIN_RECEIVED_TOTAL_DASH = CHAIN_RECEIVED_TOTAL_DASH + address_received_total_dash
            CHAIN_RECEIVED_TOTAL_US = CHAIN_RECEIVED_TOTAL_US + address_received_total_us
            
            address_sent_total_dash = float(payee["total_sent"])
            address_sent_total_us = float(payee["total_sent"]) * COINMARKET_DASH_PRICE
            CHAIN_SENT_TOTAL_DASH = CHAIN_SENT_TOTAL_DASH + address_sent_total_dash
            CHAIN_SENT_TOTAL_US = CHAIN_SENT_TOTAL_US + address_sent_total_us
            
            address_final_total_dash = float(payee["final_balance"])
            address_final_total_us = float(payee["final_balance"]) * COINMARKET_DASH_PRICE

            # loop and calc all paywment here
            address_deposit_total_dash = 0.0
            address_deposit_total_us = 0.0
            for pay in payee["payments"] :
                  if (debug): print(str(pay["amount"]) + " * "
                                    + str(pay["dash_price"])
                                    + " Dash => "
                                    + str(pay["amount"]*pay["dash_price"]) + " USD")
                  address_deposit_total_dash = address_deposit_total_dash + pay["amount"]
                  address_deposit_total_us = address_deposit_total_us + pay["amount"]*pay["dash_price"]
            PAYWALL_DEPOSIT_TOTAL_DASH = PAYWALL_DEPOSIT_TOTAL_DASH + address_deposit_total_dash
            PAYWALL_DEPOSIT_TOTAL_US = PAYWALL_DEPOSIT_TOTAL_US + address_deposit_total_us

            if (details):
                  data_out[payee["address"]] = {"Dash Chain Received" : str(format(round(address_received_total_dash,4), '.4f')) ,
                                                "Dash Chain Sent" : str(format(round(address_sent_total_dash,4), '.4f')) ,
                                                "Dash Chain Final" : str(format(round(address_final_total_dash,4), '.4f')) ,
                                                "Dash Paywall Deposit" : str(format(round(address_deposit_total_dash,4), '.4f')) ,
                                                "USD Chain Received" : str(format(round(address_received_total_us,2), '.2f')),
                                                "USD Chain Sent" : str(format(round(address_sent_total_us,2), '.2f')),
                                                "USD Chain Final" : str(format(round(address_final_total_us,2), '.2f')),
                                                "USD Paywall Deposit" : str(format(round(address_deposit_total_us,2), '.2f'))}
            else :
                  data_out[payee["address"]] = {"Dash Chain Received" : str(format(round(address_received_total_dash,4), '.4f')) ,
                                                "Dash Paywall Deposit" : str(format(round(address_deposit_total_dash,4), '.4f')) ,
                                                "USD Paywall Deposit" : str(format(round(address_deposit_total_us,2), '.2f'))}

      print("Content-Type: text/html\n\n")
      print("<html><head><title>Paywall Report</title><body><h3>Paywall Address Report</h3>")
      print("<pre>")
      print()
      print("---------------")
      for key in data_out:
            blanaced = data_out[key]["Dash Chain Received"] == data_out[key]["Dash Paywall Deposit"]
            if (details) :
                  print("<a href=\"https://chainz.cryptoid.info/dash/address.dws?" + str(key) + "\" target=\"_blank\" rel=\"noopener\">" + str(key) + "</a> - ")
                  if (blanaced) :
                        print("<pre>" + json.dumps(data_out[key], sort_keys=True, indent=4) + "</pre>")
                  else:
                        print("<font color='red'><pre>" + json.dumps(data_out[key], sort_keys=True, indent=4) + "</pre></font>")
            else :
                  if (blanaced) :                  
                        print("<a href=\"https://chainz.cryptoid.info/dash/address.dws?" + str(key) + "\" target=\"_blank\" rel=\"noopener\">" + str(key) + "</a> - "
                              + "" + str(data_out[key]["Dash Paywall Deposit"]) + " Dash; "
                              + "" + str(data_out[key]["USD Paywall Deposit"]) + " USD; "
                        )
                  else :
                        print("<a href=\"https://chainz.cryptoid.info/dash/address.dws?" + str(key) + "\" target=\"_blank\" rel=\"noopener\">" + str(key) + "</a> - "
                              + "<font color='red'>" + str(data_out[key]["Dash Paywall Deposit"]) + " Dash</font>; "
                              + "" + str(data_out[key]["USD Paywall Deposit"]) + " USD; "
                        )                        
      print("---------------")
      print("Notes:")
      print("  'USD Paywall Deposit' is calculated based on the deposit capture price, not the current Dash price.")
      print("  '<font color='red'>Red</font>' text above denotes an address imbalance between the paywall and blockchain; it should be investigated.")
      print()
      print("FILE                          - " + dirname(abspath(__file__)) + "/" + src_file)
      print("CHAIN_RECEIVED_TOTAL_DASH     - " + str(format(round(CHAIN_RECEIVED_TOTAL_DASH,4), '.4f')))
      print("CHAIN_SENT_TOTAL_DASH         - " + str(format(round(CHAIN_SENT_TOTAL_DASH,4), '.4f')))
      print("PAYWALL_DEPOSIT_TOTAL_DASH    - " + str(format(round(PAYWALL_DEPOSIT_TOTAL_DASH,4), '.4f')))
      print()
      print("CHAIN_RECEIVED_TOTAL_US       - " + str(format(round(CHAIN_RECEIVED_TOTAL_US,2), '.2f')))
      print("CHAIN_SENT_TOTAL_US           - " + str(format(round(CHAIN_SENT_TOTAL_US,2), '.2f')))      
      print("PAYWALL_DEPOSIT_TOTAL_US      - " + str(format(round(PAYWALL_DEPOSIT_TOTAL_US,2), '.2f')))
      print()
      print("Completed without error at : " + str(datetime.now())
            + "; Current Dash price in USD [" + str("%.2f" % COINMARKET_DASH_PRICE) + "]")
      print("</pre></body></html>")
      return

def do_csv_output(candidates,src_file,debug):
      COINMARKET_DASH_PRICE = get_dash_price(debug)
      CHAIN_RECEIVED_TOTAL_DASH = 0.0      
      CHAIN_RECEIVED_TOTAL_US = 0.0
      CHAIN_SENT_TOTAL_DASH = 0.0      
      CHAIN_SENT_TOTAL_US = 0.0
      PAYWALL_DEPOSIT_TOTAL_DASH = 0.0      
      PAYWALL_DEPOSIT_TOTAL_US = 0.0
      data_out = []
      payee_keys = candidates.keys()
      for key in payee_keys:
            payee = candidates[key]

            address_received_total_dash = float(payee["total_received"])
            address_received_total_us = float(payee["total_received"]) * COINMARKET_DASH_PRICE
            CHAIN_RECEIVED_TOTAL_DASH = CHAIN_RECEIVED_TOTAL_DASH + address_received_total_dash
            CHAIN_RECEIVED_TOTAL_US = CHAIN_RECEIVED_TOTAL_US + address_received_total_us
            
            address_sent_total_dash = float(payee["total_sent"])
            address_sent_total_us = float(payee["total_sent"]) * COINMARKET_DASH_PRICE
            CHAIN_SENT_TOTAL_DASH = CHAIN_SENT_TOTAL_DASH + address_sent_total_dash
            CHAIN_SENT_TOTAL_US = CHAIN_SENT_TOTAL_US + address_sent_total_us
            
            address_final_total_dash = float(payee["final_balance"])
            address_final_total_us = float(payee["final_balance"]) * COINMARKET_DASH_PRICE

            # loop and calc all paywment here
            address_deposit_total_dash = 0.0
            address_deposit_total_us = 0.0
            for pay in payee["payments"] :
                  if (debug): print(str(pay["amount"]) + " * "
                                    + str(pay["dash_price"])
                                    + " Dash => "
                                    + str(pay["amount"]*pay["dash_price"]) + " USD")
                  address_deposit_total_dash = address_deposit_total_dash + pay["amount"]
                  address_deposit_total_us = address_deposit_total_us + pay["amount"]*pay["dash_price"]
            PAYWALL_DEPOSIT_TOTAL_DASH = PAYWALL_DEPOSIT_TOTAL_DASH + address_deposit_total_dash
            PAYWALL_DEPOSIT_TOTAL_US = PAYWALL_DEPOSIT_TOTAL_US + address_deposit_total_us

            data_out.append(str(payee["address"]) + ","
                            + str(format(round(address_received_total_dash,4), '.4f')) + ","
                            + str(format(round(address_sent_total_dash,4), '.4f')) + ","
                            + str(format(round(address_final_total_dash,4), '.4f')) + ","
                            + str(format(round(address_deposit_total_dash,4), '.4f')) + ","
                            + str(format(round(address_received_total_us,2), '.2f')) + ","
                            + str(format(round(address_sent_total_us,2), '.2f')) + "," 
                            + str(format(round(address_final_total_us,2), '.2f')) + ","
                            + str(format(round(address_deposit_total_us,2), '.2f')) + ","
                            + str(format(round(address_received_total_dash,4), '.4f') == format(round(address_deposit_total_dash,4), '.4f')))


      data_out.append("")

      PAYWALL_TOTAL_DASH = 0.0      
      PAYWALL_TOTAL_US = 0.0
      data_qtr_out = {}      
      payee_keys = candidates.keys()
      for key in payee_keys:
            payee = candidates[key]
            # loop and calc all paywment here
            for pay in payee["payments"] :
                  if (debug) : print(str(payee["address"]) + " -> " + str(pay["completed_quarter"])
                        + " -> (" + str(pay["amount"]) + " * " + str(pay["dash_price"]) + ") Dash => " + str(pay["amount"]*pay["dash_price"]) + " USD")
                  PAYWALL_TOTAL_DASH = PAYWALL_TOTAL_DASH + pay["amount"]
                  PAYWALL_TOTAL_US = PAYWALL_TOTAL_US + pay["amount"]*pay["dash_price"]
                  if (pay["completed_quarter"] in data_qtr_out) :
                        qtr_dash = float(data_qtr_out[pay["completed_quarter"]]["Dash"])
                        qtr_us = float(data_qtr_out[pay["completed_quarter"]]["USD"])
                        data_qtr_out[pay["completed_quarter"]] = {"Dash" : str(format(round(pay["amount"]+qtr_dash,4), '.4f')) ,
                                                              "USD" : str(format(round((pay["amount"]*pay["dash_price"])+qtr_us,2), '.2f'))}
                  else:
                        #first find of qtr
                        data_qtr_out[pay["completed_quarter"]] = {"Dash" : str(format(round(pay["amount"],4), '.4f')) ,
                                                              "USD" : str(format(round(pay["amount"]*pay["dash_price"],2), '.2f'))}
                                    
      print("Content-Type: text/csv\n\n")
      print("address,received_total_dash,sent_total_dash,final_total_dash,deposit_paywall_total_dash,received_total_us,sent_total_us," 
                            + "final_total_us,deposit_paywall_total_us,chain=paywall?")
      for line in data_out:
            print(line)

      print("quarter,dash,usd")
      for key in sorted(data_qtr_out):
            print("'" + str(key) + "," + str(data_qtr_out[key]["Dash"]) + ","  + str(data_qtr_out[key]["USD"]))
      return

def report_output(json_directory, json_file, debug):
      json_dir = json_directory
      addr_filename = json_file
      src_file = os.path.join(json_dir, addr_filename)
      
      debug = str2bool(debug)
      
      form = cgi.FieldStorage()
      if (debug): print(str(form.getvalue("WP")))

      wp = False
      if (form.getvalue("WP") is None):
            wp = False
      else:
            wp = str2bool(form.getvalue("WP"))

      qtr_report = False
      if (form.getvalue("QTR") is None):
            qtr_report = False
      else:
            qtr_report = str2bool(form.getvalue("QTR"))

      details = False
      if (form.getvalue("DETAILS") is None):
            details = False
      else:
            details = str2bool(form.getvalue("DETAILS"))

      csv = False
      if (form.getvalue("CSV") is None):
            csv = False
      else:
            csv = str2bool(form.getvalue("CSV"))
            
      completed_quarter = "" if not form.getvalue("completed_quarter") else form.getvalue("completed_quarter")
      completed_quarter_curr = "" if not form.getvalue("completed_quarter_curr") else form.getvalue("completed_quarter_curr")
      
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

      candidates = db["pay_to"]
      candidates = get_dash_chain_totals(candidates.keys(),db["pay_to"],debug)

      if (wp):
            do_wp_output(candidates,debug)
      elif (qtr_report):
            do_qtr_output(candidates,completed_quarter,completed_quarter_curr,src_file,debug)
      elif (csv):
            do_csv_output(candidates,src_file,debug)
      else:
            do_html_output(candidates,src_file,details,debug)
            

            
if __name__ == "__main__":
      try:
            if(len(sys.argv) == 4):
                  report_output(sys.argv[1],sys.argv[2],sys.argv[3])
            else:
                  report_output(WEB_JSON_DIR,WEB_JSON_FILE,WEB_DEBUG)
                  
      except Exception as e:
            print("Exception: ",e)
            raise
