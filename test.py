#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64

s = 'echo "===Audit Result===";echo "NAME ROLE SUBJECT";kubectl get clusterrolebindings -o=custom-columns=NAME:.metadata.name,ROLE:.roleRef.name,SUBJECT:.subjects[*].name|grep cluster-admin| sed \'s/[ ]\+/ /g\';echo "===Audit Result===";'
b = s.encode('UTF-8')
bytes_encode = base64.b64encode(b)
print(bytes_encode)