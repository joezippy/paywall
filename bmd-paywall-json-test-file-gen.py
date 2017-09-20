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
json_str ='{"trans":[{"address":"XXXXXXXXXMM46w1LBmwuEdMd9iBfT6Zgnc","filled":false,"timestamp_ms":1505874716},{"address":"XwfGtKEnCMM46w1LBmwuEdMd9iBfT6Zgnc","filled":false,"timestamp_ms":1505874716},{"address":"XoaMiFGJqP3Z8mwTwZxQwmcf9VPJntwMZh","filled":false,"timestamp_ms": "' + str(time_ms) + '"},{"address":"Xxujzjy5M9Npb2gMnkm4FoCSY1BW4CmuNr","filled":false,"timestamp_ms":1505874716},{"address":"Xatnv9qKmpFhadqGEq9uigTaKT2tZRYrH7","filled":false,"timestamp_ms":1505874716},{"address":"XoagMEJrQ1DKZso2CH34q5NjsWiWVwZqox","filled":false,"timestamp_ms":1505874716},{"address":"XoagMEJrQ1DKZso2CH34q5NjsWiWVwZqox","filled":false,"timestamp_ms":1505874716},{"address":"Xig9wkobYDUGJYqY5R2aApQE2AVRz1aFAS","filled":false,"timestamp_ms":1505874716},{"address":"Xs6SqEZG4xMEBRtpCHn9VZiWVKxzegWbrL","filled":false,"timestamp_ms":1505874716},{"address":"XsWbrL","filled":false,"timestamp_ms":1505874716},{"address":"","filled":false,"timestamp_ms":1505874716},{"address":"XwfGtKEnCMM46w1LBmwuEdMd9iBfT6Zgnc","filled":true,"timestamp_ms":1505874716},{"address":"XsWbrL","filled":true,"timestamp_ms":1505874716},{"address":"","filled":true,"timestamp_ms":1505874716},{"address":"XwfGtKEnCMM46w1LBmwuEdMd9iBfT6Zgnc","filled":true,"timestamp_ms":1505874716},{"address":"XsWbrL","filled":true,"timestamp_ms":1505874716},{"address":"","filled":true,"timestamp_ms":1505874716}]}'

json_object = json.loads(json_str)

#for item in json_object["trans"]:
#    print(item)

with open('african-address-file.txt', 'w') as outfile:
    json.dump(json_object, outfile, indent=2)

print("done.")
