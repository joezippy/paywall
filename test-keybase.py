#!/usr/bin/python3
import os, cgi, cgitb, json, time, datetime, requests, subprocess, re, sys

print("Content-Type: text/plain")
print()
print("testing keybase")

from bmdjson import check_address

signature = "BEGIN KEYBASE SALTPACK SIGNED MESSAGE. kXR7VktZdyH7rvq v5weRa0zkSjiJmm 8dzt8BnSF7QPfAy AmWtlYORgWXP5hk aXmzZHPBPoIRpYD qsXcl0JX7RT65NS KLnnW8kwG9ujBNt r2bd6GNLnp4xVMr btCVAG2TMDpNhVf yXSbZmzQDnE6mIM Y4oS4YGVbw244Je Bc7lmO6225Gu6tj HgIwRnLz975GBZU Bc3GLDyRpvTEGXr AzRtx0gMk2FzHxf 2oimZKG. END KEYBASE SALTPACK SIGNED MESSAGE."

vals = check_address(signature)
vals = [item.strip() for item in vals.split(';')]
for idx, val in enumerate(vals):
    print("[" + str(idx) + "] = ", val)

print("end.")
