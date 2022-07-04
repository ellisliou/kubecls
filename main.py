import csv
from parseYaml import checks, parsed_yaml_file
from connect import *
import re
import glob
import yaml

f = open('output.csv', 'w')
writer = csv.writer(f)
f_ch5_test = open('ch5_test.txt', 'w')

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
"/bin/ps -ef | grep kube-apiserver | grep -v grep":"_k8s_api"
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

def main():
    benchMarks = loadAllTest()
    for i in range(len(benchMarks)):
        runTest(benchMarks[i])

    ch5_yaml = open('./ch5_policies_specific.yaml')
    ch5_yaml = yaml.load(ch5_yaml, Loader=yaml.FullLoader)
    #yf = parsed_yaml_file(ch5_yaml)
    ch5Yf=k8s_config_check(ch5_yaml)
    count=0
    for k in range(ch5Yf.getMaxId()):
        for i in range(ch5Yf.getMaxSubId(k)):
            ch5Yf.check = k8sChecks(k,i,ch5_yaml,configYamlList)
            f_ch5_test.writelines([ch5Yf.check.id+"\n",ch5Yf.check.text+"\n"])
            f_ch5_test.write("===Audit Result===\n")
            f_ch5_test.writelines(ch5Yf.check.line)
            f_ch5_test.write("===Audit Result===\n\n")
            count+=1
            #print(count)


if __name__ == "__main__":
    main()
