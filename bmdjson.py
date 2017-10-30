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

ansi_escapes = [
    (re.compile(r"\x1b[^m]+m") , ''), # remove ansi color sequences
    (re.compile(r'&[^;]+;') , ''),     # remove xml-encoded utf-8 chars
    (re.compile(r'b\'') , ''),         # remove stringified python bytes type wrapper
]
#    "sig_by": "\u001b[1mkcolussi\u001b[22m (you)",


def escape_ansi_utf8(string):
    string = string.decode('unicode_escape')
    string = str(string.encode('ascii', 'xmlcharrefreplace'))
    for (pattern, replace_with) in ansi_escapes:
        string = pattern.sub(replace_with, string)
    return string



def escape_ansi_for_add_address(line):
    ansi_escape = re.compile(r'\\n')
    temp_add = ansi_escape.sub('', str(line))
        
    ansi_escape = re.compile(r'\\')
    temp_add = ansi_escape.sub('', str(temp_add))
    
    ansi_escape = re.compile(r'b\'')
    temp_add = ansi_escape.sub('', str(temp_add))
    
    ansi_escape = re.compile(r'\'')
    temp_add = ansi_escape.sub('', str(temp_add))
    
    return temp_add


def check_address(encrypted_text):
    """ returns 
        {'sig_good': True, 'sig_addr': 'XjGkTLrgVxQnBy2wX12tfQiBrYQb7S7CVt', 'sig_by': 'kcolussi'}
        or
        {'sig_good': False, 'sig_addr': False, 'sig_by': False} """

    cmd = 'keybase verify -m "%s" 2>&1' % encrypted_text

    retcode, stdout = None, None
    try:
        proc = Popen(cmd, shell=True, stdout=PIPE, )
        stdout, stderr = proc.communicate()
        stdout = escape_ansi_utf8(stdout)
        retcode = proc.wait()
    except Exception as e:
        print("command %s died happily doing: %s" % (cmd, str(e)))

    # uncomment below to see the command and returns from keybase
    # print("**** cmd = " + str(cmd))
    # print("**** vals = " + str(stdout))
    extract_patterns = {
        'sig_good' : re.compile(r'Signature\s(verified)\.'),
        'sig_by'   : re.compile(r'Signed\sby\s([\w]+)'),
        'sig_addr' : re.compile(r'(X[a-zA-Z1-9]{33,34})'),
    }
    result = {k:False for k,v in extract_patterns.items()}
    if retcode == 0:
        for pat in extract_patterns:
            result[pat] = False
            match = extract_patterns[pat].search(stdout)
            if match is not None:
                if len(match.groups()) > 0:
                    result[pat] = pat == 'sig_good' and True or match.group(1)
    return result


def get_sha512_32_hash(string):
    return hashlib.sha512(string.encode('ascii')).hexdigest()[:32]

def add_address(wallet_address, json_file, your_keybase_user):
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

    cmd = 'keybase sign -m %s 2>&1' % wallet_address
    import hashlib
    db_key = get_sha512_32_hash(wallet_address)
    #print(db_key)
    proc = Popen(cmd, shell=True, stdout=PIPE, )
    stdout, stderr = proc.communicate()
    signature = escape_ansi_for_add_address(stdout)
    #print("keybase say: %s" % signature)
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
        "keybase_user": str(your_keybase_user),
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
        #print("Number of addresses in the file = %s" % len(db['pay_to'].keys()))
        data_file.seek(0)
        data_file.write(json.dumps(db, sort_keys=True, indent=2))

        
if __name__ == "__main__":
    #def add_address(wallet_address, json_file, your_keybase_user):
    try:
        if(len(sys.argv) <= 3):
            print("Wallet address, output json file, keybase_user_id required on the command-line.")
        if(len(sys.argv) == 4):
            add_address(sys.argv[1],sys.argv[2],sys.argv[3])
        if(len(sys.argv) > 5 ):
            print("Only 3 args allowed on the command-line.")
                        
    except Exception as e:
        print("Exception: ",e)
        raise
