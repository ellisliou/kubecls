import paramiko
import getpass
import json
import yaml
import re
import glob
import argparse

global pass1,clair_IP

def runAudit(num, command):
    #print(command+"\n")
    input, output, e = ssh.exec_command(command)
    if command[0:7]=="sudo -S":
        input.write(pass1+ "\n")
        input.flush()
    line=output.readlines()
    if len(line) == 0:
        #line.insert(0,"")
        line=e.readlines()
    return line
def getclairIP():
    return clair_IP

parser = argparse.ArgumentParser()
parser.add_argument("-TargetedIP", help="Target IP address of kubernetes you want to login via ssh connection)")
parser.add_argument("-Username", help="User name to login via ssh connection")
parser.add_argument("-Password", help="Password to login via ssh connection")
parser.add_argument("-image_scan_IP", help="Server IP of image vulnerability scanning")
args = parser.parse_args()

clair_IP=args.image_scan_IP

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#pass1 = getpass.getpass('Please input password to login via ssh connection: ')
pass1=args.Password
ssh.connect(hostname=args.TargetedIP, username=args.Username, password=args.Password, allow_agent = 'true', timeout=10)
print('[*]Login successfully with SSH connection ')
#print(runAudit(0,"/usr/local/kubernetes/current/stage2/usr/bin/kubectl config view"))

class k8s_config_check:
    def __init__(self,yf):
        self.yaml = yf["groups"]

    def secret_check(self,compareStr,comareItem,configYamlList):
        secretList=""
        if "/" in compareStr:
            compareStr_list=compareStr.split("/")
        else:
            compareStr_list=[compareStr]
        if configYamlList[3] is None: #k8s_ClusterRoles
            self.items=""
        else:
            self.items=configYamlList[3]["items"]
            self.binding=configYamlList[1]["items"]
        if self.items!="":
            secretList="**ClusterRoles**\nUser_Name ClusterRole_Name apiGroups verbs\n"
            for i in range(len(self.items)):
                for k in range(len(self.items[i]["rules"])):
                    if comareItem in self.items[i]["rules"][k]:
                        for p in range(len(compareStr_list)):
                            if compareStr_list[p] in self.items[i]["rules"][k][comareItem]:
                                secretList=outputConcate(secretList,self.binding,self.items[i],k)
        
        if configYamlList[4] is None: #k8s_Roles
            self.items=""
        else:
            self.items=configYamlList[4]["items"]
            self.binding=configYamlList[2]["items"]
        if self.items:
            secretList=secretList+"\n**Roles**\nUser_Name Role_Name apiGroups verbs\n"
            for i in range(len(self.items)):
                for k in range(len(self.items[i]["rules"])):
                    if comareItem in self.items[i]["rules"][k]:
                        if compareStr in self.items[i]["rules"][k][comareItem]:
                            secretList=outputConcate(secretList,self.binding,self.items[i],k)
        return secretList

    def twoItem_check(self,compareStr,comareItem,compareStr2,comareItem2,configYamlList):
        secretList=""
        
        if configYamlList[3] is None: #k8s_ClusterRoles
            self.items=""
        else:
            self.items=configYamlList[3]["items"]
            self.binding=configYamlList[1]["items"]
        if self.items!="":
            secretList="**ClusterRoles**\nUser_Name ClusterRole_Name apiGroups verbs\n"
            for i in range(len(self.items)):
                for k in range(len(self.items[i]["rules"])):
                    self.rules=self.items[i]["rules"][k]
                    if comareItem in self.rules and comareItem2 in self.rules:
                        if compareStr in self.rules[comareItem] and compareStr2 in self.rules[comareItem2]:
                            secretList=outputConcate(secretList,self.binding,self.items[i],k)
        
        if configYamlList[4] is None: #k8s_Roles
            self.items=""
        else:
            self.items=configYamlList[4]["items"]
            self.binding=configYamlList[2]["items"]
        if self.items:
            secretList=secretList+"\n================================================================\n**Roles**\nUser_Name Role_Name apiGroups verbs\n"
            for i in range(len(self.items)):
                for k in range(len(self.items[i]["rules"])):
                    self.rules=self.items[i]["rules"][k]
                    if comareItem in self.rules and comareItem2 in self.rules:
                        if compareStr in self.rules[comareItem] and compareStr2 in self.rules[comareItem2]:
                            secretList=outputConcate(secretList,self.binding,self.items[i],k)
        return secretList

    def serviceaccounts(self,audit_name,configYamlList):
        secretList=""
        if configYamlList[5] is None: #k8s_serviceaccounts
            self.items=""
        else:
            self.items=configYamlList[5]["items"]
        if self.items!="":
            secretList="**Service_Accounts**\nName Namespace secrets\n"
            for i in range(len(self.items)):
                if self.items[i]["metadata"]["name"]==audit_name:
                    secretList=secretList+self.items[i]["metadata"]["name"]+"  "
                    secretList=secretList+self.items[i]["metadata"]["namespace"]+"  "
                    if "secrets" in self.items[i]:
                        for k in range(len(self.items[i]["secrets"])):
                            secretList=secretList+self.items[i]["secrets"][k]["name"]
                            if (k+1)!=len(self.items[i]["secrets"]):secretList=secretList+","
                    else:
                        secretList=secretList+" NULL"
                    secretList=secretList+"\n"
        return secretList

    def automountServiceAccountTokenCheck(self,configYamlList):
        secretList=""
        if configYamlList[6] is None: #k8s_pods
            self.items=""
        else:
            self.items=configYamlList[6]["items"]
        if self.items!="":
            secretList="**Pods**\npod_Name Namespace\n"
            for i in range(len(self.items)):
                if "automountServiceAccountToken" not in self.items[i]["spec"]:
                    secretList=secretList+self.items[i]["metadata"]["name"]+"  "
                    secretList=secretList+self.items[i]["metadata"]["namespace"]+"  "
                    secretList=secretList+"\n"
                elif self.items[i]["spec"]["automountServiceAccountToken"]==true:
                    secretList=secretList+self.items[i]["metadata"]["name"]+"  "
                    secretList=secretList+self.items[i]["metadata"]["namespace"]+"  "
                    secretList=secretList+"\n"
        
        if configYamlList[5] is None: #k8s_serviceaccounts
            self.items=""
        else:
            self.items=configYamlList[5]["items"]
        if self.items!="":
            secretList=secretList+"================================================\n**Service_Accounts**\nName Namespace secrets\n"
            for i in range(len(self.items)):
                if "automountServiceAccountToken" not in self.items[i]:
                    secretList=secretList+self.items[i]["metadata"]["name"]+"  "
                    secretList=secretList+self.items[i]["metadata"]["namespace"]+"  "
                    secretList=secretList+"\n"
                elif self.items[i]["automountServiceAccountToken"]==true:
                    secretList=secretList+self.items[i]["metadata"]["name"]+"  "
                    secretList=secretList+self.items[i]["metadata"]["namespace"]+"  "
                    secretList=secretList+"\n"
        return secretList

    def pspcheck(self,compareStr,configYamlList):
        secretList=""
        if configYamlList[7] is None or configYamlList[7].get("items") is None: #k8s_psp
            self.items=""
        else:
            self.items=configYamlList[7]["items"]

        secretList="**PodSecurityPolicy**\n"
        for i in range(len(self.items)):
            if compareStr in self.items[i]['spec']:
                if compareStr=="runAsUser":
                    if self.items[i]['spec'][compareStr]["rule"]=="RunAsAny":
                        secretList=secretList+"PSP_Name runAsUser\n"+self.items[i]["metadata"]["name"]+"  RunAsAny\n"
                    elif self.items[i]['spec'][compareStr]["rule"]=="MustRunAs":
                        if self.items[i]['spec'][compareStr]["ranges"][0]["min"]=="0":
                            secretList=secretList+"PSP_Name runAsUser\n"+self.items[i]["metadata"]["name"]+"  "+listToStr(self.items[i]['spec'][compareStr])+"\n"
                elif compareStr=="requiredDropCapabilities":
                    if not(("ALL" in self.items[i]['spec'][compareStr]) or ("NET_RAW" in self.items[i]['spec'][compareStr])):
                        secretList=secretList+"PSP_Name requiredDropCapabilities\n"+self.items[i]["metadata"]["name"]+"  "+listToStr(self.items[i]['spec'][compareStr])+"\n"
                elif compareStr=="allowedCapabilities":
                    if self.items[i]['spec'][compareStr] is not None:
                        secretList=secretList+"PSP_Name allowedCapabilities\n"+self.items[i]["metadata"]["name"]+"  "+listToStr(self.items[i]['spec'][compareStr])+"\n"
                elif self.items[i]['spec'][compareStr] is True:
                    secretList=secretList+"PSP_Name\n"+self.items[i]["metadata"]["name"]+"\n"
            elif compareStr=="requiredDropCapabilities":
                secretList=secretList+"PSP_Name requiredDropCapabilities\n"+self.items[i]["metadata"]["name"]+" requiredDropCapabilities not be setted\n"
        return secretList

    def apicheck(self,compareStr,configYamlList):
        secretList=""
        if configYamlList[8] is not None:
            apiDict={}
            tmpstrList=configYamlList[8].split("--")
            for i in range(1,len(tmpstrList)):
                tmp2strList=tmpstrList[i].split("=")
                if i==len(tmpstrList)-1:
                    apiDict[tmp2strList[0]]=tmp2strList[1]
                elif len(tmp2strList)!=1:
                    apiDict[tmp2strList[0]]=tmp2strList[1][0:-1]
        if apiDict is not None and compareStr in apiDict: #k8s_api
            secretList=secretList+apiDict[compareStr]+"\n"
        else:
            secretList=secretList+"admission-control-config-file is not setted!\n"
        return secretList

    def privateKeyLength(self,configYamlList):
        secretList=""
        directoryList=runAudit(0,"find /etc/kubernetes/pki/ -name \*.key -type f")
        for i in range(len(directoryList)):
            keyContent=runAudit(0,"sudo -S openssl rsa -in "+directoryList[i][0:-1]+" -noout -text|grep \"Private-Key\"")
            secretList=secretList+directoryList[i][0:-1]+" : "+keyContent[0]
        return secretList

    def privateKeyAlgorithmh(self,configYamlList):
        secretList=""
        directoryList=runAudit(0,"find /etc/kubernetes/pki/ -name \*.crt -type f")
        for i in range(len(directoryList)):
            keyContent=runAudit(0,"sudo -S openssl x509 -in "+directoryList[i][0:-1]+" -noout -text|grep \"Signature Algorithm\"")
            secretList=secretList+directoryList[i][0:-1]+" : "+keyContent[0]
        return secretList

    def getMaxId(self):
        return len(self.yaml)

    def getMaxSubId(self,id):
        return len(self.yaml[id]["checks"])

class k8sChecks(k8s_config_check):
    def __init__(self, id ,sub_id ,yf,configYamlList):
        super().__init__(yf)
        self.it = self.yaml[id]["checks"][sub_id]
        if "id" in self.it:
            self.id = self.it["id"]
            self.type="CIS"
        elif "3GPP818id" in self.it:
            self.id = self.it["3GPP818id"]
            self.type="3GPP818"
        self.text = self.it["text"]
        if "audit" in self.it:
            self.audit = self.it["audit"]
            self.line = runAudit(self.id,self.audit)
        elif "audit_function" in self.it:
            if self.it["audit_function"] == "secret_check":
                self.line =self.secret_check(self.it["compareStr"],self.it["comareItem"],configYamlList)
            elif self.it["audit_function"] == "twoItem_check":
                self.line =self.twoItem_check(self.it["compareStr"],self.it["comareItem"],self.it["compareStr2"],self.it["comareItem2"],configYamlList)
            elif self.it["audit_function"] == "serviceaccounts":
                self.line =self.serviceaccounts(self.it["audit_name"],configYamlList)
            elif self.it["audit_function"] == "automountServiceAccountToken":
                self.line =self.automountServiceAccountTokenCheck(configYamlList)
            elif self.it["audit_function"] == "pspcheck":
                self.line =self.pspcheck(self.it["compareStr"],configYamlList)
            elif self.it["audit_function"] == "apicheck":
                self.line =self.apicheck(self.it["compareStr"],configYamlList)
            elif self.it["audit_function"] == "privateKeyLength":
                self.line =self.privateKeyLength(configYamlList)
            elif self.it["audit_function"] == "privateKeyAlgorithmh":
                self.line =self.privateKeyAlgorithmh(configYamlList)
        else:
            self.line =""

def outputConcate(secretList,binding,items,k):
    bindingNameList=getBindingUserName(binding,items["metadata"]["name"])
    for p in range(len(bindingNameList)):
        secretList=secretList+bindingNameList[p]+"  "
        secretList=secretList+items["metadata"]["name"]+"  "
        if "apiGroups" in items["rules"][k]:
            secretList=secretList+listToStr(items["rules"][k]["apiGroups"])+"  "
        else:
            secretList=secretList+"NONE  "
        secretList=secretList+listToStr(items["rules"][k]["verbs"])+"\n"
    return secretList

def getBindingUserName(BindingYaml,roleName):
    nameList=[]
    for i in range(len(BindingYaml)):
        if BindingYaml[i]["roleRef"]["name"]==roleName:
            nameList.append(BindingYaml[i]["metadata"]["name"])
    return nameList

def listToStr(list):
    tmpstr="["
    for item in list:
        tmpstr=tmpstr+","+item
    return tmpstr+"]"
