#!/usr/bin/python3

import cgi
import cgitb
import datetime
import hashlib
import json
import os
import re
import requests
import sys
import time

from subprocess import Popen, PIPE, STDOUT, call

############################################################################
# File: bmdjson.py
# Repository: https://github.com/joezippy/bmd-paywall
# Requirements: Python 3.5, webserver and CGI optional
#
# echo "XwvUKX7i5gBGa8Kqy8oQPL88vyGiauYwDt" | keybase encrypt kcolussi
####### cmd = 'keybase decrypt -i ./text.signed 2>&1'
check_addr_url = "https://explorer.dash.org/chain/Dash/q/checkaddress/"
check_addr_resp_errs = ['X5', 'SZ', 'CK']

def completed_quarter(dt):
    prev_quarter_map = ((4, -1), (1, 0), (2, 0), (3, 0))
    quarter, yd = prev_quarter_map[(dt.month - 1) // 3]
    return (dt.year + yd, quarter)

def check_address(encrypted_text):
    return encrypted_text

def get_sha512_32_hash(string):
    return hashlib.sha512(string.encode('ascii')).hexdigest()[:32]

def add_address(wallet_address, json_file):
    url = check_addr_url + wallet_address
    r = requests.get(url)
    #print("chainz say: %s" % r.text)

    if (r.status_code != requests.codes.ok):
        print("Dash blockchain explorer address check status failed.  -> " + str(r.raise_for_status()))    
        print("Address was not valid... ")
        return

    if (r.text in check_addr_resp_errs):
        print("Address was not valid... ")
        return

    import hashlib
    db_key = get_sha512_32_hash(wallet_address)
    #print(db_key)
    signature = wallet_address

    print("{\"timestamp_ms\": 1505874716,\"address\": \"" +
          str(signature) + "\",\"filled\": false},")
    address_dir = "."
    address_filename = json_file
    blank_address_filename = "blank.json"

    src_file = os.path.join(address_dir, address_filename)

    if (not os.path.isfile(src_file)):
        with open(src_file, 'w') as data_file:
            data_file.write('{"settings":{},"pay_to":{}}')
            # implicit close when exiting with clause

    address_entry = {
        "active": True,
        "address": str(wallet_address),
        "address_signature": str(signature),
        "address_balance" : float(0.0),
        "payments": [],
        "ts_created": int(time.time())
    }

    with open(src_file, 'r+') as data_file:
        db = json.load(data_file)
        if 'pay_to' not in db:
            db['pay_to'] = {}
        if db_key not in db['pay_to']:
            db['pay_to'][db_key] = address_entry
        data_file.seek(0)
        data_file.write(json.dumps(db, sort_keys=True, indent=2))

        
if __name__ == "__main__":
    #def add_address(wallet_address, json_file):
    try:
        if(len(sys.argv) <= 2):
            print("wallet-address, output-json-file required on the command-line.")
        if(len(sys.argv) == 3):
            add_address(sys.argv[1],sys.argv[2])
        if(len(sys.argv) > 3 ):
            print("Only wallet-address, output-json-file allowed on the command-line.")
                        
    except Exception as e:
        print("Exception: ",e)
        raise
