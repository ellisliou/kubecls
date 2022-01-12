import paramiko
import csv

ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host = '192.168.30.68'
user = 'k'
pass1 = 'pp1234'

ssh.connect(hostname=host, username=user, password=pass1, allow_agent = False)
'''
stdin, stdout, stderr =ssh.exec_command('sudo -i')
stdin.write('pp1234')
stdin.flush()
stdin, stdout, stderr =ssh.exec_command('id')
print(stdout.readlines())
'''

f = open('output.csv', 'w')
writer = csv.writer(f)

def write_to_csv(ssh,item_number,item_name,command):
	
	i, o, e = ssh.exec_command(command)
	i.write('pp1234'+ "\n")
	i.flush()
	line=o.readlines()
	print(item_number,item_name,line[0])
	list_tmp=[item_number,item_name,line[0][:-1]]
	writer.writerow(list_tmp)

def main():
	
	write_to_csv(ssh,"1.1.1","Ensure that the API server pod  specification file permissions are set to 644 or more restrictive",'sudo -S stat -c %a /etc/kubernetes/manifests/kube-apiserver.yaml')
	write_to_csv(ssh,"1.1.2","Ensure that the API server pod specification file ownership 設置為 root:root",'sudo -S stat -c %U:%G /etc/kubernetes/manifests/kube-apiserver.yaml')	

if __name__ == "__main__":
    main()

