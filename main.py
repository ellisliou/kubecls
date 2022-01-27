from tabnanny import check
import paramiko
import csv
from object import testItem
from parseYaml import checks, parsed_yaml_file
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host = '192.168.223.128'
user = 'root'
pass1 = '1234'
ssh.connect(hostname=host, username=user, password=pass1, allow_agent = False)

def main():
    yf = parsed_yaml_file()
    for k in range(yf.getMaxId()):
        for i in range(yf.getMaxSubId(k)):
            yf.check = checks(k,i)
            print(yf.check.execute(),yf.check.id, yf.check.text)            

if __name__ == "__main__":
    main()
