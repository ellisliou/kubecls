import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.223.128', username='root', password='1234', allow_agent = False)

def runAudit(command):
    input, output, e = ssh.exec_command(command)
    line=output.readlines()
    if len(line) == 0:
        line.insert(0,"")
    return line
