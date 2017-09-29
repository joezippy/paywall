#!/usr/bin/python3
import os, cgi, cgitb, json, time, datetime, requests, subprocess, re, sys

############################################################################
# File: verify.py
# Repository: https://github.com/joezippy/bmd-paywall
# Requirements: Python 3.5, webserver and CGI optional
#
# echo "XwvUKX7i5gBGa8Kqy8oQPL88vyGiauYwDt" | keybase encrypt kcolussi
####### cmd = 'keybase decrypt -i ./text.signed 2>&1'

try:
    if(len(sys.argv) <= 1):
        print("Encrypted signature required on the command-line.")
    if(len(sys.argv) == 2):
        from bmdjson import check_address
        vals = check_address(sys.argv[1])

        vals = [item.strip() for item in vals.split(';')]
        for idx, val in enumerate(vals):
            print("[" + str(idx) + "] = ", val)
                
    if(len(sys.argv) > 3 ):
        print("Only signature allowed on the command-line.")
        exit
        
except Exception as e:
        print("Exception: ",e)
        raise

