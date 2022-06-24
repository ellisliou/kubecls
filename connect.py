import paramiko
import getpass
import json
import yaml
import re
import glob

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#pass1 = getpass.getpass('password: ')
pass1='12'
ssh.connect(hostname='192.168.118.209', username='k', password=pass1, allow_agent = False)

file = open('./clusterrole.yaml')

def runAudit(num, command):
        input, output, e = ssh.exec_command(command)
        line=output.readlines()
        if len(line) == 0:
            line.insert(0,"")
        return line

class k8s_config_check:
    def __init__(self):
        self.node = runAudit(0,"kubectl get no -o yaml")
        file = open('k8s_node.yaml', 'w')
        file.writelines(self.node)
        file = open('./k8s_node.yaml')
        self.node = yaml.load(file, Loader=yaml.FullLoader)
        
        self.clusterrolebindings = runAudit(0,"kubectl get clusterrolebindings -o yaml")
        file = open('k8s_clusterrolebindings.yaml', 'w')
        file.writelines(self.clusterrolebindings)

        self.rolebinding = runAudit(0,"kubectl get rolebinding -o yaml")
        file = open('k8s_rolebinding.yaml', 'w')
        file.writelines(self.rolebinding)
        
        self.ClusterRoles = runAudit(0,"kubectl get ClusterRoles -o yaml")
        file = open('k8s_ClusterRoles.yaml', 'w')
        file.writelines(self.ClusterRoles)
        file = open('./k8s_ClusterRoles.yaml')
        self.ClusterRoles = yaml.load(file, Loader=yaml.FullLoader)
        
        self.Roles = runAudit(0,"kubectl get Roles -o yaml")
        file = open('k8s_Roles.yaml', 'w')
        file.writelines(self.Roles)
        file = open('./k8s_Roles.yaml')
        self.Roles = yaml.load(file, Loader=yaml.FullLoader)

    def secret_check(self,compareStr,comareItem):
        #5.1.2 Minimize access to secrets
        self.items=self.ClusterRoles["items"]
        if self.items!="":
            secretList="**ClusterRoles**\nName apiGroups verbs\n"
            for i in range(len(self.items)):
                for j in range(len(self.items[i]["rules"])):
                    if comareItem in self.items[i]["rules"][j]:
                        if compareStr in self.items[i]["rules"][j][comareItem]:
                            secretList=secretList+self.items[i]["metadata"]["name"]
                            if "apiGroups" in self.items[i]["rules"][j]:
                                secretList=secretList+listToStr(self.items[i]["rules"][j]["apiGroups"])
                            else:
                                secretList=secretList+" "
                            secretList=secretList+listToStr(self.items[i]["rules"][j]["verbs"])+"\n"
        self.items=self.Roles["items"]
        if self.items:
            secretList=secretList+"\n**Roles**\nName apiGroups verbs\n"
            for i in range(len(self.items)):
                for j in range(len(self.items[i]["rules"])):
                    if "resources" in self.items[i]["rules"][j]:
                        if "secrets" in self.items[i]["rules"][j]["resources"]:
                            secretList=secretList+self.items[i]["metadata"]["name"]
                            secretList=secretList+listToStr(self.items[i]["rules"][j]["apiGroups"])
                            secretList=secretList+listToStr(self.items[i]["rules"][j]["verbs"])+"\n"
        return secretList

def listToStr(list):
    tmpstr="["
    for item in list:
        tmpstr=tmpstr+","+item
    return tmpstr+"]"
