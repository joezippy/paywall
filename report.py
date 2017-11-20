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

def do_html_output(candidates,src_file,debug):
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
            data_out[payee["address"]] = {"Dash" : str(format(round(address_total_dash,4), '.4f')) ,
                                          "USD" : str(format(round(address_total_us,2), '.2f'))}

      print("Content-Type: text/html\n\n")
      print("<html><head><title>Paywall Report</title><body><h3>Paywall Address Report</h3>")
      print("<pre>")
      print()
      print("---------------")
      for key in data_out:
            print("<a href=\"https://chainz.cryptoid.info/dash/address.dws?" + str(key) + "\" target=\"_blank\" rel=\"noopener\">"
                  + str(key) + "</a> - " + str(data_out[key]))
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

      if (wp):
            do_wp_output(candidates,debug)
      elif (qtr_report):
            do_qtr_output(candidates,completed_quarter,completed_quarter_curr,src_file,debug)
      else:
            do_html_output(candidates,src_file,debug)
            

            
if __name__ == "__main__":
      try:
            if(len(sys.argv) == 4):
                  report_output(sys.argv[1],sys.argv[2],sys.argv[3])
            else:
                  report_output(WEB_JSON_DIR,WEB_JSON_FILE,WEB_DEBUG)
                  
      except Exception as e:
            print("Exception: ",e)
            raise
