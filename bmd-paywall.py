#!/usr/bin/python3
import os, cgi, cgitb, json, time, datetime, requests

############################################################################
# File: bmd-paywall.py
# Version: 1.0.1 (beta)
# Repository: https://github.com/joezippy/bmd-paywall
# Requirements: Python 3.5, webserver and CGI optional
#
# The bmd-paywall.py file was create to help with dash tipping and allow wallet
# automation regarding "top-ups" which could be use in a varity of ways in the
# community to pay it forward.
#
# You can find the creator of this tool in the dash slack my the name of joezippy
# Additional documentation and this file can be found in the repository
#
# Enjoy!
############################################################################

#########
# This turns the output level up
debug = False
#########

#########
# This is where we define the location of the address file
# address_dir = "/keybase/public/kcolussi/"
address_dir = "/var/www/html/"
#########

#########
# This is the filename
# address_filename = "african-address-file.txt"
address_filename = "african-address-file.txt"
#########


#########
# This is the #depost_max 
deposit_max = .1
deposit_max = round(deposit_max,6)
#########


#########
# This defines the max_pmt_freq in min
# The time.time() function returns the number of seconds since the epoch as seconds in UTC.
# https://www.epochconverter.com/
# 60 ms / min
# 3600 ms / hr
# 86400 ms / day
pmt_freq_ms = 180
next_pmt_ms = int(1505874716)
#########


#########
# This defines the blockchain explorer that will be use to fetch the amt received by the address
# the JSON file address will be concatinated on the end
expl_url = "https://explorer.dash.org/chain/Dash/q/getreceivedbyaddress/"
#########

##### start #####
src_file = address_dir + address_filename

print("Content-Type: text/plain")
print()
if (debug): print ("using file = " + src_file)

#########
# read source
#########
with open(src_file) as data_file:    
    json_object = json.load(data_file)


#########
# process addresses here
#########
bad_addrs=list()
dup_addrs=list()

for i in range(len(json_object["trans"])):
    if (json_object["trans"][i]["address"] == "" 
        or len(json_object["trans"][i]["address"]) != 34):
         bad_addrs.append(json_object["trans"][i]["address"])
    else:
        clean_addr = json_object["trans"][i]["address"]
        # check for addr dups here
        cnt_dup = 0
        for j in range(len(json_object["trans"])):
            if(json_object["trans"][j]["address"] == clean_addr):
                cnt_dup = cnt_dup + 1
        if (cnt_dup > 1):
            dup_addrs.append(json_object["trans"][i]["address"])
        else:
            if (debug): print("clean_addr =>" + clean_addr + "<")
            # check refresh next
            last_pmt_ms = json_object["trans"][i]["timestamp_ms"]
            if (last_pmt_ms == ""):
                last_pmt_ms = int(0)
            else:
                last_pmt_ms = int(last_pmt_ms)
            next_pmt_ms = int(round(last_pmt_ms,0) + int(pmt_freq_ms))
            if (debug): print("last_pmt_ms + pmt_freq_ms : " + str(last_pmt_ms) + " + " + str(pmt_freq_ms) + " = " + str(next_pmt_ms))
            if (debug): print("next_pmt_ms < time.time() -->> " + str(next_pmt_ms < round(time.time(),0)))
            if (next_pmt_ms < round(time.time(),0)):
                # check balance
                url = expl_url + clean_addr
                r = requests.get(url)
                if (r.status_code == requests.codes.ok):
                    expl_amt = float(r.text)
                    if (debug): print("expl_amt > deposit_max -> " + str(expl_amt) + " > "
                                      + str(deposit_max) + " >> " + str(expl_amt > deposit_max))
                    if (expl_amt > deposit_max):
                        # set full
                        json_object["trans"][i]["timestamp_ms"] = int(round(time.time(),0))
                        json_object["trans"][i]["filled"] = True
                        json.dumps(json_object)
                        if (debug): print(clean_addr + " - " + str(expl_amt) + " setting full")
                    else:
                        # this wallet needs to be topped off
                        json_object["trans"][i]["timestamp_ms"] = int(round(time.time(),0))
                        json_object["trans"][i]["filled"] = False
                        json.dumps(json_object)
                        if (debug): print(clean_addr + " ->>> needs "
                                          + str(round(deposit_max - expl_amt ,6)) + " to be full.")
                else:
                    print("Dash blockchain explorer address check status failed.  ->"
                          + r.raise_for_status())

########
# print warnings and clean bad addrs from the json before writting to stdout or the file
########
print()
if (len(bad_addrs) > 0 or len(dup_addrs) > 0):
    print("*************************************************************************")
    print("***            Warning removing these invalid addreses                ***")
    print("*************************************************************************")
    for i in range(len(bad_addrs)):
        bad_addr = bad_addrs[i]
        print ("bad addr [" + str(i) + "] ->" + bad_addr + "<")
        for j in range(len(json_object["trans"])):
            if(json_object["trans"][j]["address"] == bad_addr):
                del json_object["trans"][j]
                break
    for i in range(len(dup_addrs)):
        dup_addr = dup_addrs[i]
        print ("dup addr [" + str(i) + "] ->" + dup_addr + "<")
        for j in range(len(json_object["trans"])):
            if(json_object["trans"][j]["address"] == dup_addr):
                del json_object["trans"][j]
                break
    print("*************************************************************************")

# write valid un-filled data out everytime
print()
print("----------  Updating balanced of those still in need. -----------------------")
print()
for i in range(len(json_object["trans"])):
    if (json_object["trans"][i]["filled"] == False):
        clean_addr = json_object["trans"][i]["address"]
        url = expl_url + clean_addr
        r = requests.get(url)
        if (r.status_code == requests.codes.ok):
            expl_amt = float(r.text)
            print(clean_addr + " -> needs "
                  + str(round(deposit_max - expl_amt ,6)) + " to be full.")
        else:
            print("Dash blockchain explorer address check status failed.  ->"
                  + r.raise_for_status())
print()
print("--------------------------------------------------------------------------")
print()
print("Note: New payment window starts "
      + datetime.datetime.fromtimestamp(next_pmt_ms).strftime('%Y-%m-%d %H:%M:%S')+ " UTC, i'll be ")
print("checking all addreses for top-ups then. Cheers for now! :)")
print()
print()
print("Completed without error at : " + str(datetime.datetime.now()))
print()
    
#########
# write changes back down
#########
with open(src_file, 'w') as outfile:
    json.dump(json_object, outfile, indent=2)

exit
