#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
from getpass import getpass
import json
import requests

uploadJson={
    "properties": {
        "delivery_mode": 2
    },
    "routing_key": "Result_Queue",
    "payload_encoding": "string"
}
uploadJson["payload"]={"test":"ss","aa":234}
print(uploadJson)
uploadUrl="http://192.168.30.102:15672/api/exchanges/%2F/amq.default/publish"
uploadHeader={"Accept":"application/json","Content-Type":"application/json"}
r = requests.post(uploadUrl,json=uploadJson,headers=uploadHeader,auth=('rabbitmq','rabbitmq'), verify=False)
print(uploadUrl, responseStatuses[r.status_code])



