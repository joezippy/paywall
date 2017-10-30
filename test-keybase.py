#!/usr/bin/python3

import cgi
import cgitb
import datetime
import json
import os
import re
import requests
import subprocess
import sys
import time

from bmdjson import check_address


print("Content-Type: text/plain\n")
print("testing keybase")

print()
print("PASS:")
signature = "BEGIN KEYBASE SALTPACK SIGNED MESSAGE. kXR7VktZdyH7rvq v5weRa0zkSjiJmm 8dzt8BnSF7QPfAy AmWtlYORgWXP5hk aXmzZHPBPoIRpYD qsXcl0JX7RT65NS KLnnW8kwG9ujBNt r2bd6GNLnp4xVMr btCVAG2TMDpNhVf yXSbZmzQDnE6mIM Y4oS4YGVbw244Je Bc7lmO6225Gu6tj HgIwRnLz975GBZU Bc3GLDyRpvTEGXr AzRtx0gMk2FzHxf 2oimZKG. END KEYBASE SALTPACK SIGNED MESSAGE."

sig_result = check_address(signature)
for k, v in sorted(sig_result.items(), key=lambda x: x[0]):
    # is saying the leftmost of the pair k,v -- alphabetic sorting of keys
    # now sig_addr, sig_by, then sig_good -- display bugged me
    print("[" + str(k) + "] = ", v)

print()
print("FAIL: Bad String")
signature2 = "BEGIN KEYBASE SALTPACK SIGNED MESSAGE. kXR7VktZdy27rvq v5weRa0zkDL3e9k D1e7HgTLY1WFWdi UfZI1s56lquWUJu lBvdIblMbFGwTGa M9oYSI9cU7KjGW9 2JOGghIjQX3Fqw5 xsvEpPo9pEuA25J Ut0J0Fur0C3F8oZ n50PAvVWVmb0iEP 5MNUBEMHMo5DTtF OhK66v3FFwu0qJe 8R35q5A5ycevVsR pdaOBQQ1VGcNIlF 9YU6a0Wi5kd85JH rjSupUZ. END KEYBASE SALTPACK SIGNED MESSAGE."

sig_result = check_address(signature2)
for k, v in sorted(sig_result.items(), key=lambda x: x[0]):
    # is saying the leftmost of the pair k,v -- alphabetic sorting of keys
    # now sig_addr, sig_by, then sig_good -- display bugged me
    print("[" + str(k) + "] = ", v)

print()
print("end.")

