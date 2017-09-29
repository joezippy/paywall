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
    if(len(sys.argv) <= 2):
        print("Encrypted address and keybase_user_id required on the command-line.")
    if(len(sys.argv) == 3):
        from bmdjson import check_address
        vals = check_address(sys.argv[1],sys.argv[2]).split(';')
        
        print("stdout split vals[0] ->" + vals[0] + "<")
        print("stdout split vals[1] ->" + vals[1] + "<")
    if(len(sys.argv) > 4 ):
        print("Only encrypted address and keybase_user_id allowed on the command-line.")
        exit
        
except Exception as e:
        print("Exception: ",e)
        raise




