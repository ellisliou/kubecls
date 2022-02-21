import paramiko
import csv
import object
import yaml
import re

#load file
a_yaml_file = open("master.yaml")
parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
ch = parsed_yaml_file["groups"]
ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host = '192.168.223.128'
user = 'test'
pass1 = '1234'

ssh.connect(hostname=host, username=user, password=pass1, allow_agent = False)

f = open('output.csv', 'w')
writer = csv.writer(f)


def write_to_csv(ssh,i,k,config):
	command = config[k]["checks"][i]["audit"]
	title = config[k]["checks"][i]["text"]
	number = config[k]["checks"][i]["id"]
	input, output, e = ssh.exec_command(command)
	line=output.readlines()
	if "type" in config[k]["checks"][i]:
		print("warn")
	else:	
		test_item = config[k]["checks"][i]["tests"]["test_items"][0]
		execute(test_item,line)
	result = [number,title,command,line]
	writer.writerow(result) 
	print(number,line)

def execute(test_item, line):
	if "compare" in test_item.keys():
		op = test_item["compare"]["op"]
		if op == "gte":
			print(op)
		elif op == "gt":
			print(op)
		elif op == "lt":
			print(op)
		elif op == "lte":
			print(op)
		elif op == "bitmask":
			print(op)
		elif op == "eq":
			print(op)
		elif op == "noteq":
			print(op)
		elif op == "has":
			print(op)

def OwnerPermissionCheck(analyte,criteria):
	result=0
	analyte_list=analyte[:-1].split(':')
	criteria_list=criteria.split(':')
	for i in range(0,2):
		if analyte_list[i]!=criteria_list[i]:
			result=1
			break
	return result

def FilePermissionCheck(analyte,criteria):
	result=0
	for i in range(0,3):
		if analyte[i]>criteria[i]:
			result=1
			break
	return result

def write_to_csv(ssh,item_number,item_name,command,criteria,check_type):
	
	i, o, e = ssh.exec_command(command)
	i.write(pass1+ "\n")
	i.flush()
	line=o.readlines()
	if check_type=="file_permission" :
		result=FilePermissionCheck(line[0],criteria)
	elif check_type=="owner_permission" :
		result=OwnerPermissionCheck(line[0],criteria)

	if line:
		print(item_number,item_name,line[0],"Compliant" if result==0 else "Not compliant")
		list_tmp=[item_number,item_name,line[0][:-1],"Compliant" if result==0 else "Not compliant"]
		writer.writerow(list_tmp)

def main():
	
	write_to_csv(ssh,"1.1.1","Ensure that the API server pod  specification file permissions are set to 644 or more restrictive",'sudo -S stat -c %a /etc/kubernetes/manifests/kube-apiserver.yaml',"644","file_permission")
	write_to_csv(ssh,"1.1.2","Ensure that the API server pod specification file ownership set to root:root",'sudo -S stat -c %U:%G /etc/kubernetes/manifests/kube-apiserver.yaml',"root:root","owner_permission")	

def main():
    for k in range(len(ch)):
        for i in range(len(parsed_yaml_file["groups"][k]["checks"])):
            write_to_csv(ssh,i,k,parsed_yaml_file["groups"])


if __name__ == "__main__":
    main()

