import paramiko
import csv
import getpass
import yaml
from pandas import json_normalize

a_yaml_file = open("master.yaml")
parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
ch = parsed_yaml_file["groups"]
ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host = '192.168.30.68'
user = 'k'
pass1 = 'pp1234'
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

	#print(number,line)

def execute(test_item, line):
	if "compare" in test_item.keys():
		op = test_item["compare"]["op"]
		if (op == "gte" || op == "gt", op == "lt", op == "lte"):
			print(op)
		elif (op == "bitmask"):
			print(op)
		elif(op == "eq"):
		
		elif(op == "noteq"):
		
		elif(op == "has"):


def main():
	for k in range(len(ch)):
		for i in range(len(parsed_yaml_file["groups"][k]["checks"])):
			write_to_csv(ssh,i,k,parsed_yaml_file["groups"])
	#if "type" in parsed_yaml_file["groups"][0]["checks"][0]:
	#	print("warn")
	#print(parsed_yaml_file["groups"][0]["checks"][0])
if __name__ == "__main__":
    main()

