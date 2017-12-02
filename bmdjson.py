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

from subprocess import Popen, PIPE, STDOUT, call, check_output

############################################################################
# File: bmdjson.py
# Repository: https://github.com/joezippy/bmd-paywall
# Requirements: Python 3.5, webserver and CGI optional
#
# echo "XwvUKX7i5gBGa8Kqy8oQPL88vyGiauYwDt" | keybase encrypt kcolussi
####### cmd = 'keybase decrypt -i ./text.signed 2>&1'
check_addr_url = "https://explorer.dash.org/chain/Dash/q/checkaddress/"
check_addr_resp_errs = ['X5', 'SZ', 'CK']

#########
# This defines the blockchain explorer that will be use to fetch the balance by the address.
# Funds have to be moved by the address owner, if you expect subsiquent deposits based on pmt_freq_ms

# the JSON file address will be concatinated on the end
# API Key (mydashdirect@gmail.com): cf3003ed342d
EXPLORER_URL = "https://chainz.cryptoid.info/dash/api.dws?q=multiaddr&n=0&key=cf3003ed342d&active="
EXPLORER_HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                   'AppleWebKit/537.36 (KHTML, like Gecko)'
                                   'Chrome/45.0.2454.101 Safari/537.36'),
                    'referer': 'https://explorer.dash.org/'}


COINMARKET_PRICE_URL = "https://api.coinmarketcap.com/v1/ticker/dash/?convert=USD"
COINMARKET_HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                   'AppleWebKit/537.36 (KHTML, like Gecko)'
                                   'Chrome/45.0.2454.101 Safari/537.36'),
                    'referer': 'https://coinmarketcap.com/'}

def completed_quarter(date):
    return date.year, int(((date.month - 1) / 3 + 1))

def encode(text):
    retcode, stdout = None, None
    out = ""
    try:
        cmd = 'echo %s |  openssl enc -des-ecb -base64 -pass file:%s' % (text,"/var/www/dash-direct/hex.key")
        proc = Popen(cmd, shell=True, stdout=PIPE, )
        stdout, stderr = proc.communicate()
        retcode = proc.wait()
    except Exception as e:
        print("command %s died happily doing: %s" % (cmd, str(e)))
    return "".join(map(chr, stdout)).replace('\n', '').replace('\r', '')


def decode(text):
    retcode, stdout = None, None
    try:
        cmd = 'echo %s | openssl enc -d -des-ecb -base64 -pass file:%s' % (text,"/var/www/dash-direct/hex.key")
        proc = Popen(cmd, shell=True, stdout=PIPE, )
        stdout, stderr = proc.communicate()
        retcode = proc.wait()
    except Exception as e:
        print("command %s died happily doing: %s" % (cmd, str(e)))
    return "".join(map(chr, stdout)).replace('\n', '').replace('\r', '')

def get_sha512_32_hash(string):
    return hashlib.sha512(string.encode('ascii')).hexdigest()[:32]

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

def get_dash_chain_totals(payee_keys,candidates,debug):
    big_url = EXPLORER_URL
    for key in payee_keys:
        payee = candidates[key]
        big_url = big_url + decode(payee["address_signature"]) + "|"
    if (debug): print("big_url = " + str(big_url))
    r = requests.get(big_url,EXPLORER_HEADERS)
    if (r.status_code == requests.codes.ok):
        data = json.loads(r.text)
        for addrs in data["addresses"]:
            key = get_sha512_32_hash(addrs["address"])
            payee = candidates[key]
            if 'total_received' not in addrs:
                payee.setdefault("total_received", 0.0)
            else:
                payee["total_received"] = float(str(addrs["total_received"] * .00000001))
                
            if 'total_sent' not in addrs:
                payee.setdefault("total_sent", 0.0)
            else:
                payee["total_sent"] = float(str(addrs["total_sent"] * .00000001))

            if 'final_balance' not in addrs:
                payee.setdefault("final_balance", 0.0)
            else:
                payee["final_balance"] = float(str(addrs["final_balance"] * .00000001))

            if (debug): print("candidates : " + json.dumps(candidates, sort_keys=True, indent=8))
    else:
        if (debug): print("Address check at " + big_url + "status failed ["
                          + str(r.status_code) + "].  -> "
                          + str(r.raise_for_status()))
    return candidates

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
    signature = encode(wallet_address)

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
