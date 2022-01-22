import paramiko
import csv
import getpass
import yaml
from pandas import json_normalize
import re

a_yaml_file = open("compare_test_item.yaml")
parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
ch = parsed_yaml_file["groups"]
test_item = ch[0]["checks"][1]["tests"]["test_items"][0]
s = "permissions=600\n"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

str1_2_1 = 'root       535   507  4  2021 ?        1-00:36:47 kube-apiserver --advertise-address=192.168.30.68 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --insecure-port=0 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/12 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key\n'

host = '192.168.30.68'
user = 'k'
pass1 = 'pp1234'
ssh.connect(hostname=host, username=user, password=pass1, allow_agent = False)

def evaluate(t,s):
    flag = t["flag"]
    match, value, err = findValue(flag, s)
    op = t["compare"]["op"]
    tCompareValue = t["compare"]["value"]
    expectedResult,testResult = compareOp(op, value, tCompareValue)
    print(expectedResult,testResult)

#compare function

def compareOp(tCompareOp, flagVal, tCompareValue):
    testResult = False
    requested = None
    if tCompareOp == "gte" or tCompareOp == "gt" or tCompareOp == "lt" or  tCompareOp == "lte":
        print(tCompareOp)
    elif tCompareOp == "bitmask":
        print(tCompareValue)
        requested = int(flagVal,8)
        inputVal = int(tCompareValue,8)
        print(requested,inputVal)
        testResult = (requested & inputVal) == requested
    elif tCompareOp == "eq":
        value = flagVal.lower()
    elif tCompareOp == "noteq":
        print(tCompareOp)
    elif tCompareOp == "has":
        print(tCompareOp)
    return requested,testResult

#get the test value 
def findValue(flag,string):
    match = flag in string
    pttn = '(' + flag + ')(=|: *)*([^\s]*) *'
    flagRe = re.compile(pttn)
    vals = flagRe.search(string)
    if vals != None:
        err = 0
        if vals[3] != "":
            value = vals[3]
        else:
            if flag.startswith("--"):
                value = "true"
            else:
                value = vals[1]
    else:
        err = 1
        value = None
    print(match,value,err)
    return match, value, err


def main():
    print(test_item)
    evaluate(test_item,str1_2_1)

if __name__ == "__main__":
    main()
