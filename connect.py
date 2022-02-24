import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.30.33', username='monitor', password='1234', allow_agent = False)

def runAudit(num, command):
    input, output, e = ssh.exec_command(command)
    line=output.readlines()
    if len(line) == 0:
        line.insert(0,"")
    return line
