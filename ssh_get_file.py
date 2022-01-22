import paramiko
import csv
import getpass
import yaml
from pandas import json_normalize
import re

#load file
a_yaml_file = open("master.yaml")
parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
ch = parsed_yaml_file["groups"]
ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host = '192.168.30.68'
user = 'k'
pass1 = 'pp1234'
ssh.connect(hostname=host, username=user, password=pass1, allow_agent = False)

testString = "['root       535   507  4  2021 ?        1-00:36:47 kube-apiserver --advertise-address=192.168.30.68 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --insecure-port=0 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/12 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key\n']"

f = open('output.csv', 'w')
writer = csv.writer(f)

def write_to_csv(ssh, i, k, config):
    command = config[k]["checks"][i]["audit"]
    title = config[k]["checks"][i]["text"]
    number = config[k]["checks"][i]["id"]
    input, output, e = ssh.exec_command(command)
    line=output.readlines()
    if "type" in config[k]["checks"][i]:
        print("warn")
    else:    
        print(number,line)
        for q in range(len(config[k]["checks"][i]["tests"]["test_items"])):
            test_item = config[k]["checks"][i]["tests"]["test_items"][q]
            evaluate(test_item,line[0])
            #execute(test_item,line[0])
    result = [number,title,command,line]
    writer.writerow(result) 
    print(number,line)

def execute(test_item, lines):
    match, value = findValue(test_item["flag"],lines)
    if "compare" in test_item.keys():
        print("test")
#evaluate function
def evaluate(t,s):
    #t:test_item[i]
    #s:audit result
    flag = t["flag"]
    match, value, err = findValue(flag, s)
    
    if "set" in t.keys() and t["set"]:
        if match and t["compare"] != "":
            op = t["compare"]["op"]
            tCompareValue = t["compare"]["value"]
            expectedResult,testResult = compareOp(op, value, tCompareValue)
            print (expectedResult,testResult)

#compare function
def compareOp(tCompareOp, flagVal, tCompareValue):
    if tCompareOp == "gte" or tCompareOp == "gt" or tCompareOp == "lt" or  tCompareOp == "lte":
        print(tCompareOp)
    elif tCompareOp == "bitmask":
        requested = int(flagfval,8)
        inputval = int(tCompareValue,8)
        testResult = (requested & inputval) == requested
        expectedResult = requested = int(flagfval,8)
    elif tCompareOp == "eq":
        print(tCompareOp)
    elif tCompareOp == "noteq":
            print(tCompareOp)
    elif tCompareOp == "has":
            print(tCompareOp)
    return expectedResult,testResult

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
    return match, value, err
    

def main():
    #write_to_csv(ssh,1,0,parsed_yaml_file["groups"])
    #print(parsed_yaml_file.["groups"][0]["checks"][0]["tests"][])
    #findValue("insecure-port",testString)

    for k in range(len(ch)):
        for i in range(len(parsed_yaml_file["groups"][k]["checks"])):
            write_to_csv(ssh,i,k,parsed_yaml_file["groups"])


if __name__ == "__main__":
    main()

