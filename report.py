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

def paywall_output(json_directory, json_file, debug):

      PAYWALL_TOTAL_DASH = 0.0      
      PAYWALL_TOTAL_US = 0.0
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
            
      if (not wp):
            if (debug): print("No WP!")
            print("Content-Type: text/plain\n")
      else:
            if (debug): print("WP!")
            print("Content-Type: text/html\n")
            
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

      if (not wp): print()
      if (not wp): print("---------------")
      if (not wp): print()      
      candidates = db["pay_to"]
      payee_keys = candidates.keys()
      for key in payee_keys:
            payee = candidates[key]
            if (debug) : print("\nBefore payments reported : " + json.dumps(payee, sort_keys=True, indent=8))
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
            if (not wp): print(str(payee["address"]) + " : "
                                        + str(format(round(address_total_dash,4), '.4f') + " Dash; "
                                        + str(format(round(address_total_us,2), '.2f') + " USD")))
            
      if (not wp): print()
      if (not wp): print("---------------")
      if (not wp): print("Notes:")
      if (not wp): print("  UDS value is calculated based on the deposit capture price, not the current Dash price.")
      if (not wp): print()
      if (not wp): print("FILE                      - "
                                  + dirname(abspath(__file__))
                                  + "/" + src_file)
      if (not wp): print("PAYWALL_TOTAL_DASH        - " + str(format(round(PAYWALL_TOTAL_DASH,4), '.4f')))
      if (not wp): print("PAYWALL_TOTAL_US          - " + str(format(round(PAYWALL_TOTAL_US,2), '.2f')))
      if (not wp): print()
      if (not wp): print("Completed without error at : " + str(datetime.now()))
      if (not wp): print()

      if (wp) :
            print("<html><body><title>Paywall Report</title><small><a href=\"")
            print("https://" + str(os.environ["HTTP_HOST"]) + str(os.environ["SCRIPT_NAME"]))
            print("\" target=\"_blank\" rel=\"noopener\">Current Paywall Totals</a>: <br>"
                  + str(round(PAYWALL_TOTAL_DASH,3)) + " Dash; "
                  + str(round(PAYWALL_TOTAL_US,2)) + " USD </small></body></html>") 
            
if __name__ == "__main__":
      # def paywall_output(json_directory, json_file, debug):
      try:
            if(len(sys.argv) == 4):
                  paywall_output(sys.argv[1],sys.argv[2],sys.argv[3])
            else:
                  paywall_output(WEB_JSON_DIR,WEB_JSON_FILE,WEB_DEBUG)
                  
      except Exception as e:
            print("Exception: ",e)
            raise
