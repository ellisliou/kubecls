#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
from getpass import getpass
import json
import requests

tmpline="k"
if tmpline.split(','):
    print(len(tmpline)+1)
    initalPass=1
    for i in range(2,len(tmpline)-1):
        print(tmpline[i].split(" ")[0])
        if tmpline[i].split(" ")[0]=="default":
            print(tmpline[i].split(" ")[0])
            initalPass=0
    print(initalPass)
