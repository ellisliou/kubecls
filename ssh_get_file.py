import paramiko
import csv
import getpass

ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host = '192.168.118.209'
user = 'k'
pass1 = getpass.getpass('password: ')

ssh.connect(hostname=host, username=user, password=pass1, allow_agent = False)

f = open('output.csv', 'w')
writer = csv.writer(f)

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

if __name__ == "__main__":
    main()

