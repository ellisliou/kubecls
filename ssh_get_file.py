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
            if len(line) > 0:
                evaluate(test_item,line[0])
    result = [number,title,command,line]
    writer.writerow(result) 
    print(number,line)

def main():
    for k in range(len(ch)):
        for i in range(len(parsed_yaml_file["groups"][k]["checks"])):
            write_to_csv(ssh,i,k,parsed_yaml_file["groups"])


if __name__ == "__main__":
    main()

