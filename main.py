import csv
from parseYaml import checks, parsed_yaml_file
from connect import *
from checkPolicy import *
from checkClair import *
from HalfautoToAuto import *
from datetime import datetime
import re
import glob
import yaml
import json
import argparse
import base64
import zipfile

global outputDirectory,clair_IP
outputDirectory={}
clair_IP=getclairIP()

f = open('output.csv', 'w')
writer = csv.writer(f)
f_ch5_test = open('ch5_test.txt', 'w')
main_log = open('main_log.txt', 'w')

main_log.write("[*]Load mapping table between 3GPP-818-ID and CIS-1.20-ID\n")
print('[*]Load mapping table between 3GPP-818-ID and CIS-1.20-ID')

configYamlList= []
k8sConfigList={
"kubectl get no -o yaml":"k8s_node",
"kubectl get clusterrolebindings -o yaml":"k8s_clusterrolebindings",
"kubectl get rolebinding -o yaml":"k8s_rolebinding",
"kubectl get ClusterRoles -o yaml":"k8s_ClusterRoles",
"kubectl get Roles -o yaml":"k8s_Roles",
"kubectl get serviceaccounts -A -o yaml":"k8s_serviceaccounts",
"kubectl get pods -A -o yaml":"k8s_pods",
"kubectl get psp -o yaml":"k8s_psp",
"/bin/ps -ef | grep kube-apiserver | grep -v grep":"k8s_api"
}
count=0
#runAudit(0,"cd /usr/local/kubernetes/current/stage2/usr/bin")
for i in range(len(k8sConfigList)):
    keyName=list(k8sConfigList.keys())[i]
    configfile = runAudit(0,keyName)
    file = open(k8sConfigList[keyName]+".yaml", 'w')
    file.writelines(configfile)
    file = open(k8sConfigList[keyName]+".yaml")
    file = yaml.load(file, Loader=yaml.FullLoader)
    configYamlList.append(file)
    count+=1
    #print(count)
print('[*]Retrieve related configuration in k8s with yaml format')
main_log.write("[*]Retrieve related configuration in k8s with yaml format\n")

def preloadConfig():
    #map_table=open("map_table.yaml")
    map_table=getPolicy("map_table")
    map_table = yaml.load(map_table, Loader=yaml.FullLoader)
    #ignore_table=open("ignore.yaml")
    ignore_table=getPolicy("ignore_table")
    ignore_table = yaml.load(ignore_table, Loader=yaml.FullLoader)
    #ch5_yaml = open("ch5_policies_specific.yaml")
    ch5_yaml = getPolicy("ch5_policy")
    ch5_yaml = yaml.load(ch5_yaml, Loader=yaml.FullLoader)
    return map_table, ignore_table, ch5_yaml

def loadAllTest():
    yamlList = []
    tmpList = ["ch1","ch2","ch3"]
    #for file in sorted(glob.glob('./cis_1_20/*.yaml')):
    for k in range(len(tmpList)):
        #file = open(file)
        file=getPolicy(tmpList[k])
        file = yaml.load(file, Loader=yaml.FullLoader)
        yamlList.append(file)
    #print(yamlList[0])
    return yamlList

def runTest(bm):
    map_table, ignore_table, ch5_yaml = preloadConfig()
    yf = parsed_yaml_file(bm)
    for k in range(yf.getMaxId()):
        for i in range(yf.getMaxSubId(k)):
            yf.check = checks(k,i,bm)
            writer.writerow([yf.check.execute(),yf.check.id, yf.check.text])
            if str(yf.check.id) in ignore_table.keys():
                #print("ignore: ",yf.check.id,"\n")
                pass
            elif str(map_table[yf.check.id]) not in outputDirectory.keys():
                outputDirectory[str(map_table[yf.check.id])]=[{'3GPP818ID':str(map_table[yf.check.id])},{'CISID': str(yf.check.id),'CISResult':yf.check.execute(),'audit output':yf.check.line}]
            else:
                outputDirectory[str(map_table[yf.check.id])]=outputDirectory[str(map_table[yf.check.id])]+[{'CISID': str(yf.check.id),'CISResult':yf.check.execute(),'audit output':yf.check.line}]
            #print(outputDirectory)

def outputVersionV1(directoryList):
    tmpdirectory ={}
    file=getPolicy("outputV1_table")
    file = yaml.load(file, Loader=yaml.FullLoader)
    keytmpList=list(file)
    for i in range(len(keytmpList)):
        tmpKey=keytmpList[i]
        directoryList[file[tmpKey]]=directoryList.pop(tmpKey)
        directoryList[file[tmpKey]][0]["3GPP818ID"]=file[tmpKey]
    return directoryList

def outputDirectorySortedResult(directoryList):
    tmpdirectory ={}
    #print(directoryList["1.6"])
    tmpList=sorted(directoryList.keys())
    for i in range(len(tmpList)):
        resultList=[]
        resultCount=0
        finalResult=""
        for x in range(1,len(directoryList[tmpList[i]])):
            CISResult=directoryList[tmpList[i]][x].get("CISResult")
            resultList.append(CISResult)
            if CISResult=="PASS":
                resultCount=resultCount+1
            elif CISResult=="WARN":
                resultCount=resultCount+2
            elif CISResult=="FAIL":
                resultCount=resultCount+100
            else:
                resultCount=resultCount+1000
        if resultCount==len(directoryList[tmpList[i]])-1:
            finalResult="PASS"
        elif resultCount<=2*(len(directoryList[tmpList[i]])-1):
            finalResult="WARN"
        elif resultCount==100*(len(directoryList[tmpList[i]])-1):
            finalResult="FAIL"
        else:
            finalResult="Manual"
        directoryList[tmpList[i]][0]['Final Result']=finalResult
        tmpdirectory[tmpList[i]]=directoryList[tmpList[i]]
        #print(tmpList[i],":",resultList,":",finalResult)
    #print(tmpdirectory[1.6])
    return tmpdirectory


def main():
    map_table, ignore_table, ch5_yaml = preloadConfig()
    if clair_IP:
        print(clair_IP)
        checkClair(clair_IP) #run clair
    benchMarks = loadAllTest()
    for i in range(len(benchMarks)):
        runTest(benchMarks[i])
    print('[*]CIS-CH1、CIS-CH2、CIS-CH3 are audited!')
    main_log.write("[*]CIS-CH1、CIS-CH2、CIS-CH3 are audited!\n")

    
    ch5Yf=k8s_config_check(ch5_yaml)
    count=0
    for k in range(ch5Yf.getMaxId()):
        for i in range(ch5Yf.getMaxSubId(k)):
            ch5Yf.check = k8sChecks(k,i,ch5_yaml,configYamlList)
            #print(ch5Yf.check.id+"\n")
            f_ch5_test.writelines([str(ch5Yf.check.id),"\n",ch5Yf.check.text,"\n"])
            f_ch5_test.write("===Audit Result===\n")
            f_ch5_test.writelines(ch5Yf.check.line)
            f_ch5_test.write("===Audit Result===\n\n")
            if str(ch5Yf.check.id) in ignore_table.keys():
                pass
            elif ch5Yf.check.type=="3GPP818":
                if str(ch5Yf.check.id) not in outputDirectory.keys():
                    outputDirectory[str(ch5Yf.check.id)]=[{'3GPP818ID':str(ch5Yf.check.id)},{'CISResult':"Manual",'audit output':ch5Yf.check.line}]
                else:
                    outputDirectory[str(ch5Yf.check.id)]=outputDirectory[str(ch5Yf.check.id)]+[{'CISResult':"Manual",'audit output':ch5Yf.check.line}]
            elif ch5Yf.check.type=="CIS":
                if str(map_table[str(ch5Yf.check.id)]) not in outputDirectory.keys():
                    outputDirectory[str(map_table[ch5Yf.check.id])]=[{'3GPP818ID':str(map_table[ch5Yf.check.id])},{'CISID': ch5Yf.check.id,'CISResult':"Manual",'audit output':ch5Yf.check.line}]
                else:
                    outputDirectory[str(map_table[ch5Yf.check.id])]=outputDirectory[str(map_table[ch5Yf.check.id])]+[{'CISID': ch5Yf.check.id,'CISResult':"Manual",'audit output':ch5Yf.check.line}]
            else:
                print(ch5Yf.check.id)
            count+=1
            #print(count)

    print('[*]CIS-CH5 completed!')
    main_log.write('[*]CIS-CH5 completed!\n')

    #tmpdirectory ={}
    #tmpdirectory=half_auto_To_auto(outputDirectory)
    #with open("origin.json", "w") as outfile:
    #    json.dump(tmpdirectory, outfile)

    #print(json.dumps(outputDirectorySortedResult(outputDirectory), indent = 4))
    with open("output_origin.json", "w") as outfile:
        json.dump(outputDirectory, outfile)

    tmpPKI={}
    tmpPKI[0]=runAudit(0,"echo ZmluZCAvZXRjL2t1YmVybmV0ZXMvcGtpLyB8IHhhcmdzIHN0YXQgLWMgImZpbGUgbmFtZSBpcyAiJW4iLCBmaWxlIG93bnNob3AgaXMgIiVVOiVH | base64 -d | sh")
    tmpPKI[1]=runAudit(0,"echo ZmluZCAvZXRjL2t1YmVybmV0ZXMvcGtpLyAtbmFtZSAnKi5jcnQnIHwgeGFyZ3Mgc3RhdCAtYyAiZmlsZSBuYW1lIGlzICIlbiIsIGZpbGUgcGVybWlzc2lvbnMgaXMgIiVh | base64 -d | sh")
    tmpPKI[2]=runAudit(0,"echo ZmluZCAvZXRjL2t1YmVybmV0ZXMvcGtpLyAtbmFtZSAnKi5rZXknIHwgeGFyZ3Mgc3RhdCAtYyAiZmlsZSBuYW1lIGlzICIlbiIsIGZpbGUgcGVybWlzc2lvbnMgaXMgIiVh | base64 -d | sh")
    tmpline=outputDirectory["1.1"][1]["audit output"][0]
    if tmpline.find("--audit-log-path")!=-1:
        audit_log=tmpline.split("--audit-log-path=")[1].split(' ')[0]
        tmpPKI[3]=runAudit(0,"stat -c %a "+audit_log)
    if tmpline.find("--audit-policy-file")!=-1:
        audit_policy=tmpline.split("--audit-policy-file=")[1].split(' ')[0]
        tmpPKI[4]=runAudit(0,"stat -c %a "+audit_policy)

    tmpdirectory ={}
    tmpdirectory=outputDirectorySortedResult(half_auto_To_auto(outputDirectory,tmpPKI))
    
    with open("output_total.json", "w") as outfile:
        json.dump(tmpdirectory, outfile)

    with open("output_v1.json", "w") as outfile:
        json.dump(outputVersionV1(tmpdirectory), outfile)

    end_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    main_log.write('scanning finish time: '+end_time+"\n")

    main_log.close()
    f.close()
    connect_log_close()
    clair_log_close()

    # with zipfile.ZipFile(end_time+'.zip', mode='w') as zf:
    #     zf.write("ch5_test.txt")
    #     zf.write("output.csv")
    #     zf.write("main_log.txt")
    #     zf.write("connect_log.txt")
    #     zf.write("clair_log.txt")
    #     zf.write("output_v1.json")
    #     zf.write("output_total.json")
    #     zf.write("k8s_api.yaml")
    #     zf.write("k8s_psp.yaml")
    #     zf.write("k8s_pods.yaml")
    #     zf.write("k8s_serviceaccounts.yaml")
    #     zf.write("k8s_Roles.yaml")
    #     zf.write("k8s_ClusterRoles.yaml")
    #     zf.write("k8s_rolebinding.yaml")
    #     zf.write("k8s_clusterrolebindings.yaml")
    #     zf.write("k8s_node.yaml")

if __name__ == "__main__":
    main()
