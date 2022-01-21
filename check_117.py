import paramiko
import csv
import getpass
import datetime

print("Execution datetime : ",datetime.datetime.now())
print("Target IP : 192.168.30.68")

ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host = '192.168.30.68'
user = 'k'
#pass1 = getpass.getpass('password: ')
pass1='pp1234'

ssh.connect(hostname=host, username=user, password=pass1, allow_agent = False)

f = open('output.csv', 'w')
writer = csv.writer(f)

def write_to_csv(ssh,item_number,item_name,command):
	
	print("\n==== ",item_name," ====")
	i, o, e = ssh.exec_command(command)
	i.write(pass1+ "\n")
	i.flush()
	line=o.readlines()
	for i in range(0,len(line)):
		print(line[i][:-1])
	#list_tmp=[item_number,item_name,line[0][:-1]]
	#writer.writerow(list_tmp)

def main():
	
	write_to_csv(ssh,"1.1.1","OS version",'sudo -S cat /etc/os-release')
	write_to_csv(ssh,"1.1.2","password policy",'sudo -S cat /etc/pam.d/common-password')
	write_to_csv(ssh,"1.1.2","sshd config",'sudo -S cat /etc/ssh/sshd_config')	

if __name__ == "__main__":
    main()

