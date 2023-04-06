import csv
from parseYaml import checks, parsed_yaml_file
from connect import *
import re
import glob
import yaml
import json
import argparse

global outputDirectory
outputDirectory={}

f = open('output.csv', 'w')
writer = csv.writer(f)
f_ch5_test = open('ch5_test.txt', 'w')
map_table=open("map_table.yaml")
map_table = yaml.load(map_table, Loader=yaml.FullLoader)
ignore_table=open("ignore.yaml")
ignore_table = yaml.load(ignore_table, Loader=yaml.FullLoader)
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

def loadAllTest():
    yamlList = []
    for file in sorted(glob.glob('./cis_1_20/*.yaml')):
    #for file in glob.glob('./*.yaml'):
        file = open(file)
        file = yaml.load(file, Loader=yaml.FullLoader)
        yamlList.append(file)
    #print(yamlList[0])
    return yamlList

def runTest(bm):
    yf = parsed_yaml_file(bm)
    for k in range(yf.getMaxId()):
        for i in range(yf.getMaxSubId(k)):
            yf.check = checks(k,i,bm)
            writer.writerow([yf.check.execute(),yf.check.id, yf.check.text])
            if str(yf.check.id) in ignore_table.keys():
                #print("ignore: ",yf.check.id,"\n")
                pass
            elif str(map_table[yf.check.id]) not in outputDirectory.keys():
                outputDirectory[str(map_table[yf.check.id])]=[{'3GPP818ID':str(map_table[yf.check.id])},{'CISID': str(yf.check.id),'CISResult':yf.check.execute(),'audit output5':yf.check.line}]
            else:
                outputDirectory[str(map_table[yf.check.id])]=outputDirectory[str(map_table[yf.check.id])]+[{'CISID': str(yf.check.id),'CISResult':yf.check.execute(),'audit output6':yf.check.line}]
            #print(outputDirectory)

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
    benchMarks = loadAllTest()
    for i in range(len(benchMarks)):
        runTest(benchMarks[i])
    print('[*]CIS-CH1、CIS-CH2、CIS-CH3 are audited!')

    ch5_yaml = open('./ch5_policies_specific.yaml')
    ch5_yaml = yaml.load(ch5_yaml, Loader=yaml.FullLoader)
    #yf = parsed_yaml_file(ch5_yaml)
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
                #print("ignore: ",ch5Yf.check.id,"\n")
                pass
            elif ch5Yf.check.type=="3GPP818":
                if str(ch5Yf.check.id) not in outputDirectory.keys():
                    outputDirectory[str(ch5Yf.check.id)]=[{'3GPP818ID':str(ch5Yf.check.id)},{'CISResult':"Manual",'audit output1':ch5Yf.check.line}]
                else:
                    outputDirectory[str(ch5Yf.check.id)]=outputDirectory[str(ch5Yf.check.id)]+[{'CISResult':"Manual",'audit output2':ch5Yf.check.line}]
            elif ch5Yf.check.type=="CIS":
                if map_table[str(ch5Yf.check.id)] not in outputDirectory.keys():
                    outputDirectory[str(map_table[ch5Yf.check.id])]=[{'3GPP818ID':str(map_table[ch5Yf.check.id])},{'CISID': ch5Yf.check.id,'CISResult':"Manual",'audit output3':ch5Yf.check.line}]
                else:
                    outputDirectory[str(map_table[ch5Yf.check.id])]=outputDirectory[str(map_table[ch5Yf.check.id])]+[{'CISID': ch5Yf.check.id,'CISResult':"Manual",'audit output4':ch5Yf.check.line}]
            count+=1
            #print(count)

    print('[*]CIS-CH5 completed!')

    #print(json.dumps(outputDirectorySortedResult(outputDirectory), indent = 4))
    with open("output.json", "w") as outfile:
        json.dump(outputDirectorySortedResult(outputDirectory), outfile)


if __name__ == "__main__":
    main()
