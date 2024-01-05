#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
from getpass import getpass
import json
import requests
import jwt
from datetime import datetime, timezone, timedelta

imageHashID="sha256:bac6081102aae54ba4bcc714695b8f637e42768c7f376f374c428bab043ddc0f"
scanResultUrl="http://192.168.30.102:6060/matcher/api/v1/vulnerability_report/"+imageHashID
responseStatuses = {200: "Website Available",301: "Permanent Redirect",302: "Temporary Redirect",404: "Not Found",500: "Internal Server Error",503: "Service Unavailable"}
jwttoken=jwt.encode({"iss": "clairctl","exp": datetime.now(tz=timezone.utc) + timedelta(seconds=60),"nbf": datetime.now(tz=timezone.utc) - timedelta(seconds=120),"iat": datetime.now(tz=timezone.utc)},"secret",algorithm="HS256")
print(jwttoken)
headers={"Authorization":"Bearer "+jwttoken}

try:
    web_response = requests.get(scanResultUrl,headers=headers,timeout=30)
    print(scanResultUrl, responseStatuses[web_response.status_code],"\n\n")
    print(web_response.text)
except:
    print("Connection error\n")