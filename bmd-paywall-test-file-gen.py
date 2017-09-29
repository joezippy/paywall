#!/usr/bin/python3

import json, time

############################################################################
# File: bmd-paywall-json-test-file-gen.py
# Repository: https://github.com/joezippy/bmd-paywall
# Requirements: Python 3.5, webserver and CGI optional
#
# The bmd-paywall-json-test-file-gen.py file was create to generate all the
# JSON test file conditions: including invalid records, full addresses, address
# needing coins and time sensitive records.  Because this input file was used
# during the test driven development, I would expect no issues while using it.
# If cases are missing please let me know so they can be added.
#
# You can find the creator of this tool in the dash slack my the name of
# joezippy. Additional documentation and this file can be found in the
# repository.
#
# Enjoy!
############################################################################

time_ms = int(round(time.time(),0))

from bmdjson import add_address

add_address("XXXXXXXXXMM46w1LBmwuEdMd9iBfT6Zgnc","foo.json","kcolussi")
add_address("XwfGtKEnCMM46w1LBmwuEdMd9iBfT6Zgnc","foo.json","kcolussi")
add_address("XoaMiFGJqP3Z8mwTwZxQwmcf9VPJntwMZh","foo.json","kcolussi")
add_address("Xxujzjy5M9Npb2gMnkm4FoCSY1BW4CmuNr","foo.json","kcolussi")
add_address("Xatnv9qKmpFhadqGEq9uigTaKT2tZRYrH7","foo.json","kcolussi")
add_address("XoagMEJrQ1DKZso2CH34q5NjsWiWVwZqox","foo.json","kcolussi")
add_address("XoagMEJrQ1DKZso2CH34q5NjsWiWVwZqox","foo.json","kcolussi")
add_address("Xig9wkobYDUGJYqY5R2aApQE2AVRz1aFAS","foo.json","kcolussi")
add_address("Xs6SqEZG4xMEBRtpCHn9VZiWVKxzegWbrL","foo.json","kcolussi")
add_address("XsWbrL","foo.json","kcolussi")
add_address("","foo.json","kcolussi")
add_address("XwfGtKEnCMM46w1LBmwuEdMd9iBfT6Zgnc","foo.json","kcolussi")
add_address("XsWbrL","foo.json","kcolussi")
add_address("","foo.json","kcolussi")
add_address("XwfGtKEnCMM46w1LBmwuEdMd9iBfT6Zgnc","foo.json","kcolussi")
add_address("XsWbrL","foo.json","kcolussi")
add_address("","foo.json","kcolussi")
print("done.")
