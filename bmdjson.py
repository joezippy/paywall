#!/usr/bin/python3
import os, cgi, cgitb, json, time, datetime, requests, subprocess, re, sys

############################################################################
# File: verify.py
# Repository: https://github.com/joezippy/bmd-paywall
# Requirements: Python 3.5, webserver and CGI optional
#
# echo "XwvUKX7i5gBGa8Kqy8oQPL88vyGiauYwDt" | keybase encrypt kcolussi
####### cmd = 'keybase decrypt -i ./text.signed 2>&1'
check_addr_url = "https://explorer.dash.org/chain/Dash/q/checkaddress/"
check_addr_resp_errs = ['X5', 'SZ', 'CK']

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

def escape_ansi_for_check_address(line):
    ansi_escape = re.compile(r'$\n')
    temp = ansi_escape.sub(';', str(line))

    ansi_escape = re.compile(r'x1b*.[0-9]?[0-9]m')
    temp = ansi_escape.sub('', str(temp))
        
    ansi_escape = re.compile(r'\\\\n')
    temp = ansi_escape.sub('.', str(temp))
        
    ansi_escape = re.compile(r'\\n')
    temp = ansi_escape.sub('', str(temp))
        
    ansi_escape = re.compile(r'\\')
    temp = ansi_escape.sub('', str(temp))
        
    ansi_escape = re.compile(r'b\'')
    temp = ansi_escape.sub('', str(temp))
        
    ansi_escape = re.compile(r'\'')
    temp = ansi_escape.sub('', str(temp))
    
    ansi_escape = re.compile(r'\.')
    temp = ansi_escape.sub(';', str(temp))

    ansi_escape = re.compile(r'\ \(you\)')
    temp = ansi_escape.sub('', str(temp))
    
    return temp

def check_address(encrypted_text):
    cmd = "keybase verify -m \"" + encrypted_text + "\" 2>&1"     
    from subprocess import Popen,PIPE,STDOUT,call
    proc=Popen(cmd, shell=True, stdout=PIPE, )
    stdout, stderr=proc.communicate()
    # print("**** cmd = " + str(cmd))
    # print("**** vals = " + str(escape_ansi(stdout)))
    return escape_ansi_for_check_address(stdout)
    

def add_address(wallet_address, json_file, your_keybase_user):
    url = check_addr_url + wallet_address
    r = requests.get(url)
    if (r.status_code == requests.codes.ok):
        if (r.text not in check_addr_resp_errs):
            cmd = "keybase sign -m " + wallet_address + " 2>&1"     
            from subprocess import Popen,PIPE,STDOUT,call
            proc=Popen(cmd, shell=True, stdout=PIPE, )
            stdout, stderr=proc.communicate()
            signature = escape_ansi_for_add_address(stdout)
            
            print("{\"timestamp_ms\": 1505874716,\"address\": \"" + str(signature) + "\",\"filled\": false},")
            address_dir = "./"
            address_filename = json_file
            blank_address_filename = "blank.json"
            src_file = address_dir + address_filename
            print("os.path.isfile(" + src_file + ") -> " + str(os.path.isfile(src_file)))
            if (os.path.isfile(src_file)): 
                with open(src_file) as data_file:    
                    json_object = json.load(data_file)
                    i = len(json_object["trans"])
                    json_object["trans"].append({'keybase_user': your_keybase_user,'timestamp_ms': int(round(time.time(),0)),'address': str(signature),'filled': False})
                    print("Number of addresses in the file = " + str(len(json_object["trans"])))
                    with open(src_file, 'w') as outfile:
                        json.dump(json_object, outfile, indent=2)
            else:
                print("Need to create this json file: " + src_file)
                os.system("wget https://raw.githubusercontent.com/joezippy/bmd-paywall/master/blank.json")
                with open(blank_address_filename) as data_file:    
                    json_object = json.load(data_file)
                    json_object["trans"][0] = ({'keybase_user': your_keybase_user,'timestamp_ms': int(round(time.time(),0)),'address': str(signature),'filled': False})
                    with open(src_file, 'w') as outfile:
                        json.dump(json_object, outfile, indent=2)
        else:
            print("Dash blockchain explorer address check status failed.  -> " + str(r.raise_for_status()))    
            print("Address was not valid... ")
            exit
    else:
        print("Address was not valid... ")
        exit
        
if __name__ == "__main__":
    #def add_address(wallet_address, json_file, your_keybase_user):
    try:
        if(len(sys.argv) <= 3):
            print("Wallet address, output json file, keybase_user_id required on the command-line.")
        if(len(sys.argv) == 4):
            add_address(sys.argv[1],sys.argv[2],sys.argv[3])
        if(len(sys.argv) > 5 ):
            print("Only 3 args allowed on the command-line.")
            exit
                        
    except Exception as e:
        print("Exception: ",e)
        raise
