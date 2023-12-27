import string

def getValue(line,parameter):
	return line.split(parameter+"=")[1].split(' ')[0]

def half_auto_To_auto(Directory,tmpPKI):
	authorizationMode=""
	enableAdmissionPlugins=""
	disableAdmissionPlugins=""
	audit_log=""
	audit_policy=""
	
	tmpline=Directory["1.1"][1]["audit output"][0]
	if tmpline.find("--audit-log-path")!=-1:
		audit_log=getValue(tmpline,"--audit-log-path")
	if tmpline.find("--audit-policy-file")!=-1:
		audit_policy=getValue(tmpline,"--audit-policy-file")

	#1.1 - 1.2.2
	tmpline=Directory["1.1"][1]["audit output"][0]
	tmpParameter="--token-auth-file"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.1"][1]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		Directory["1.1"][1]["audit output"][0]=tmpParameter+"參數設定為"+getValue(tmpline,tmpParameter)+"\n"

	#1.1 - 1.2.6
	tmpline=Directory["1.1"][2]["audit output"][0]
	tmpParameter="--authorization-mode"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.1"][2]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		authorizationMode=getValue(tmpline,tmpParameter)
		if authorizationMode.find("AlwaysAllow")==-1:
			Directory["1.1"][2]["audit output"][0]=tmpParameter+"參數設定為"+authorizationMode+", 並未設定參數為AlwaysAllow\n"
		else:
			Directory["1.1"][2]["audit output"][0]=tmpParameter+"參數設定為"+authorizationMode+", 並已設定參數為AlwaysAllow\n"

	#1.1 - 1.2.7
	if authorizationMode.find("Node")==-1:
		Directory["1.1"][3]["audit output"][0]=tmpParameter+"參數設定為"+authorizationMode+", 並未設定參數為Node\n"
	else:
		Directory["1.1"][3]["audit output"][0]=tmpParameter+"參數設定為"+authorizationMode+", 並已設定參數包含Node\n"

	#1.1 - 1.2.8
	if authorizationMode.find("RBAC")==-1:
		Directory["1.1"][4]["audit output"][0]=tmpParameter+"參數設定為"+authorizationMode+", 並未設定參數為RBAC\n"
	else:
		Directory["1.1"][4]["audit output"][0]=tmpParameter+"參數設定為"+authorizationMode+", 並已設定參數包含RBAC\n"

	#1.2 - 1.2.1
	if Directory["1.2"][1]["audit output"][0].find("--anonymous-auth=true")==-1:
		Directory["1.2"][1]["CISResult"]="PASS"
		Directory["1.2"][1]["audit output"][0]="--anonymous-auth參數未設定為true\n"
	else:
		Directory["1.2"][1]["audit output"][0]="--anonymous-auth參數設定為true\n"

	#1.3 - 1.2.32
	tmpline=Directory["1.3"][1]["audit output"][0]
	tmpParameter="--encryption-provider-config"
	if Directory["1.3"][1]["audit output"][0].find(tmpParameter)==-1:
		Directory["1.3"][1]["CISResult"]="FAIL"
		Directory["1.3"][1]["audit output"][0]="--encryption-provider-config參數未設定\n"
	else:
		Directory["1.3"][1]["audit output"][0]="--encryption-provider-config參數設定為"+getValue(tmpline,tmpParameter)+", 請確認encryption-provider-config設定檔案是否符合系統需求\n"

	#1.4 - 1.2.10
	tmpline=Directory["1.4"][1]["audit output"][0]
	tmpParameter="--enable-admission-plugins"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.4"][1]["CISResult"]="FAIL"
		Directory["1.4"][1]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		enableAdmissionPlugins=getValue(tmpline,tmpParameter)
		if enableAdmissionPlugins.find("AlwaysAdmit")==-1:
			Directory["1.4"][1]["audit output"][0]=tmpParameter+"參數設定為"+getValue(tmpline,tmpParameter)+", 並未設定參數為AlwaysAdmit\n"
		else:
			Directory["1.4"][1]["audit output"][0]=tmpParameter+"參數設定為"+getValue(tmpline,tmpParameter)+", 並已設定參數為AlwaysAdmit\n"

	#1.5 - 1.2.25
	if Directory["1.5"][1]["audit output"][0].find("--request-timeout")==-1:
		Directory["1.5"][1]["CISResult"]="PASS"
		Directory["1.5"][1]["audit output"][0]="--request-timeout參數未設定\n"
	else:
		setValue=60
		setValue=int(getValue(Directory["1.5"][1]["audit output"][0],"--request-timeout="))
		if setValue>=60:
			Directory["1.5"][1]["CISResult"]="PASS"
		else:
			Directory["1.5"][1]["comment"]="請確認request-timeout設定是否符合系統需求\n"

	#1.6 - 1.2.13
	tmpline=Directory["1.6"][1]["audit output"][0]
	tmpParameter="--disable-admission-plugins"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.6"][1]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		disableAdmissionPlugins=getValue(tmpline,tmpParameter)
		if disableAdmissionPlugins.find("ServiceAccount")==-1:
			Directory["1.6"][1]["audit output"][0]=tmpParameter+"參數設定為"+disableAdmissionPlugins+", 並未設定參數為ServiceAccount\n"
		else:
			Directory["1.6"][1]["audit output"][0]=tmpParameter+"參數設定為"+disableAdmissionPlugins+", 並已設定參數為ServiceAccount\n"

	#1.6 - 1.2.14
	tmpline=Directory["1.6"][2]["audit output"][0]
	tmpParameter="--disable-admission-plugins"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.6"][2]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		disableAdmissionPlugins=getValue(tmpline,tmpParameter)
		if disableAdmissionPlugins.find("NameSpaceLifycycle")==-1:
			Directory["1.6"][2]["audit output"][0]=tmpParameter+"參數設定為"+disableAdmissionPlugins+", 並未設定參數包含NameSpaceLifycycle\n"
		else:
			Directory["1.6"][2]["audit output"][0]=tmpParameter+"參數設定為"+disableAdmissionPlugins+", 並設定參數包含NameSpaceLifycycle\n"

	#1.6 - 1.2.16
	tmpline=Directory["1.6"][3]["audit output"][0]
	tmpParameter="--enable-admission-plugins"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.6"][3]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		if enableAdmissionPlugins.find("NodeRestriction")==-1:
			Directory["1.6"][3]["audit output"][0]=tmpParameter+"參數設定為"+enableAdmissionPlugins+", 並未設定參數包含NodeRestriction\n"
		else:
			Directory["1.6"][3]["audit output"][0]=tmpParameter+"參數設定為"+enableAdmissionPlugins+", 並已依規範設定參數包含NodeRestriction\n"

	#1.6 - 1.2.17
	tmpline=Directory["1.6"][4]["audit output"][0]
	tmpParameter="--insecure-bind-address"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.6"][4]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		Directory["1.6"][4]["audit output"][0]=tmpParameter+"參數設定為"+getValue(tmpline,tmpParameter)+"\n"

	#1.6 - 1.2.19
	tmpline=Directory["1.6"][5]["audit output"][0]
	tmpParameter="--secure-port"
	if tmpline.find(tmpParameter)==-1:
		Directory["1.6"][5]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		Directory["1.6"][5]["audit output"][0]=tmpParameter+"參數設定為"+getValue(tmpline,tmpParameter)+"\n"

	#1.7 - 1.2.26
	tmpItem="1.7"
	tmpline=Directory[tmpItem][1]["audit output"][0]
	tmpParameter="--service-account-lookup"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][1]["audit output"][0]=tmpParameter+"參數未設定, 系統默認生效\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		if tmpActualConfig.find("true")!=-1:
			Directory[tmpItem][1]["audit output"][0]=tmpParameter+"參數設定為"+tmpActualConfig+"\n"
		elif tmpActualConfig.find("false")!=-1:
			Directory[tmpItem][1]["audit output"][0]=tmpParameter+"參數設定為"+tmpActualConfig+"\n"

	#1.7 - 1.2.27
	tmpItem="1.7"
	tmpIndex=2
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter="--service-account-key-file"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定, 公鑰檔案未設定\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數設定為"+tmpActualConfig+"\n"

	#1.7 - 1.2.28
	tmpItem="1.7"
	tmpIndex=3
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter1="--etcd-certfile"
	tmpParameter2="--etcd-keyfile"
	if tmpline.find(tmpParameter1)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter1+"參數未設定, 憑證檔案未設定\n"
	else:
		tmpActualConfig1=getValue(tmpline,tmpParameter1)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter1+"參數設定為"+tmpActualConfig1+"\n"
	if tmpline.find(tmpParameter2)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=Directory[tmpItem][tmpIndex]["audit output"][0]+"\n"+tmpParameter2+"參數未設定, 密鑰檔案未設定\n"
	else:
		tmpActualConfig2=getValue(tmpline,tmpParameter2)
		Directory[tmpItem][tmpIndex]["audit output"][0]=Directory[tmpItem][tmpIndex]["audit output"][0]+"\n"+tmpParameter2+"參數設定為"+tmpActualConfig2+"\n"

	#1.7 - 1.2.31
	tmpItem="1.7"
	tmpIndex=4
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter="--etcd-cafile"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定, 憑證頒發機構文件參數未設定\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數設定為"+tmpActualConfig+"\n"

	#2.2 - 1.1.14
	Directory["2.2"][1]["audit output"][0]="admin.conf檔案擁有者權限設置為： "+Directory["2.2"][1]["audit output"][0]
	#2.2 - 1.1.16
	Directory["2.2"][2]["audit output"][0]="scheduler.conf檔案擁有者權限設置為： "+Directory["2.2"][2]["audit output"][0]
	#2.2 - 1.1.18
	Directory["2.2"][3]["audit output"][0]="controller-manager.conf檔案擁有者權限設置為： "+Directory["2.2"][3]["audit output"][0]

	#2.4 - 1.2.21
	auditlog_result=1
	tmpItem="2.4"
	tmpIndex=1
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter="--audit-log-path"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定, 稽核記錄檔案參數未設定\n"
		auditlog_result=0
	elif int(tmpPKI[3][0])<=644:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"稽核記錄檔案參數設定為"+tmpActualConfig+" , 且稽核記錄檔案之檔案權限設定為"+tmpPKI[3][0].strip()
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"稽核記錄檔案參數設定為"+tmpActualConfig+" , 且稽核記錄檔案之檔案權限設定為"+tmpPKI[3][0]
		Directory["2.4"][0]["Final Result"]="FAIL"

	#2.5 - 1.2.3
	tmpItem="2.5"
	tmpline=Directory[tmpItem][1]["audit output"][0]
	tmpParameter="--kubelet-https"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][1]["audit output"][0]=tmpParameter+"參數未設定, 系統默認生效\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][1]["audit output"][0]=tmpParameter+"參數設定為"+tmpActualConfig+"\n"

	#2.5 - 1.2.4
	tmpItem="2.5"
	tmpIndex=2
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter1="--kubelet-client-certificate"
	tmpParameter2="--kubelet-client-key"
	if tmpline.find(tmpParameter1)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter1+"參數未設定, 憑證檔案未設定\n"
	else:
		tmpActualConfig1=getValue(tmpline,tmpParameter1)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter1+"參數設定為"+tmpActualConfig1+"\n"
	if tmpline.find(tmpParameter2)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=Directory[tmpItem][tmpIndex]["audit output"][0]+"\n"+tmpParameter2+"參數未設定, 金鑰檔案未設定\n"
	else:
		tmpActualConfig2=getValue(tmpline,tmpParameter2)
		Directory[tmpItem][tmpIndex]["audit output"][0]=Directory[tmpItem][tmpIndex]["audit output"][0]+"\n"+tmpParameter2+"參數設定為"+tmpActualConfig2+"\n"

	#2.5 - 1.2.29
	tmpItem="2.5"
	tmpIndex=3
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter1="--tls-cert-file"
	tmpParameter2="--tls-private-key-file"
	if tmpline.find(tmpParameter1)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter1+"參數未設定, 憑證檔案未設定\n"
	else:
		tmpActualConfig1=getValue(tmpline,tmpParameter1)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter1+"參數設定為"+tmpActualConfig1+"\n"
	if tmpline.find(tmpParameter2)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=Directory[tmpItem][tmpIndex]["audit output"][0]+"\n"+tmpParameter2+"參數未設定, 密鑰檔案未設定\n"
	else:
		tmpActualConfig2=getValue(tmpline,tmpParameter2)
		Directory[tmpItem][tmpIndex]["audit output"][0]=Directory[tmpItem][tmpIndex]["audit output"][0]+"\n"+tmpParameter2+"參數設定為"+tmpActualConfig2+"\n"

	#2.5 - 1.2.30
	tmpItem="2.5"
	tmpIndex=4
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter="--client-ca-file"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定, 憑證參數未設定\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"憑證參數設定為"+tmpActualConfig+"\n"

	#2.5 - 2.3
	tmpItem="2.5"
	tmpIndex=5
	tmpline=Directory[tmpItem][tmpIndex]["audit output"]
	tmpSpecLine=""
	tmpParameter="--auto-tls"
	for i in range(len(tmpline)):
		if tmpline[i].find("etcd --")!=-1:
			tmpSpecLine=tmpline[i]
			del Directory[tmpItem][tmpIndex]["audit output"]
			Directory[tmpItem][tmpIndex]["audit output"]=[""]
	if tmpSpecLine.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數設定為"+getValue(tmpSpecLine,tmpParameter)+"\n"

	#2.5 - 2.6
	tmpItem="2.5"
	tmpIndex=6
	tmpline=Directory[tmpItem][tmpIndex]["audit output"]
	tmpSpecLine=""
	tmpParameter="--peer-auto-tls"
	for i in range(len(tmpline)):
		if tmpline[i].find("etcd --")!=-1:
			tmpSpecLine=tmpline[i]
			del Directory[tmpItem][tmpIndex]["audit output"]
			Directory[tmpItem][tmpIndex]["audit output"]=[""]
	if tmpSpecLine.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定\n"
	else:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數設定為"+getValue(tmpSpecLine,tmpParameter)+"\n"

	#2.6 - 1.1.5
	tmpItem="2.6"
	tmpIndex=1
	Directory[tmpItem][tmpIndex]["audit output"][0]="kube-scheduler.yaml檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#2.6 - 1.1.11
	tmpItem="2.6"
	tmpIndex=2
	Directory[tmpItem][tmpIndex]["audit output"][0]="etcd data 資料夾權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#2.6 - 1.1.13
	tmpItem="2.6"
	tmpIndex=3
	Directory[tmpItem][tmpIndex]["audit output"][0]="admin.conf檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#2.6 - 1.1.15
	tmpItem="2.6"
	tmpIndex=4
	Directory[tmpItem][tmpIndex]["audit output"][0]="scheduler.conf檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#2.6 - 1.1.17
	tmpItem="2.6"
	tmpIndex=5
	Directory[tmpItem][tmpIndex]["audit output"][0]="controller-manager.conf檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	
	#3.1 - 3.2.1
	Directory["3.1"]=Directory["3.1"]+[{}]
	Directory["3.1"][2]["CISID"]="1.2.21"
	if auditlog_result==1:
		Directory["3.1"][2]["CISResult"]="PASS"
	else:
		Directory["3.1"][2]["CISResult"]="FAIL"
	tmpline=Directory["3.1"][1]["audit output"]
	tmpSpecLine=""
	for i in range(len(tmpline)):
		if tmpline[i].find("kube-apiserver --")!=-1:
			tmpSpecLine=tmpline[i]
			del Directory["3.1"][1]["audit output"]
			tmpline=Directory["3.1"][1]["audit output"]=[""]
	if tmpSpecLine.find("--audit-policy-file")==-1:
		Directory["3.1"][1]["CISResult"]="FAIL"
		Directory["3.1"][1]["audit output"][0]="--audit-policy-file參數未設定，稽核政策未設定\n"
		auditlog_result=0
	else:
		Directory["3.1"][1]["audit output"][0]="--audit-policy-file參數設定為"+getValue(tmpSpecLine,"--audit-policy-file")+", 請確認audit-policy-file設定是否符合系統需求\n"
	Directory["3.1"][2]["audit output"]=[""]
	Directory["3.1"][2]["audit output"][0]=Directory["2.4"][1]["audit output"][0]
	if auditlog_result==1:
		Directory["3.1"][0]["Final Result"]="PASS"
	else:
		Directory["3.1"][0]["Final Result"]="FAIL"

	#4.1
	tmpline=Directory["4.1"][1]["audit output"]
	if tmpline.find(" Private-Key: (")!=-1:
		tmplist=tmpline.split("\n")
		initalPass=1
		for i in range(len(tmplist)-1):
			if int(tmplist[i].split("Private-Key: (")[1].split(" bit")[0])<2048:
				initalPass=0
		if initalPass==1:
			Directory["4.1"][1]["CISResult"]="PASS"
		else:
			Directory["4.1"][1]["CISResult"]="FAIL"
		del Directory["4.1"][1]["audit output"]
		Directory["4.1"][1]["audit output"]=[""]
		Directory["4.1"][1]["audit output"][0]="金鑰檔案資訊如下：\n"+tmpline
	else:
		del Directory["4.1"][1]["audit output"]
		Directory["4.1"][1]["audit output"]=[""]
		Directory["4.1"][1]["audit output"][0]="未發現金鑰檔案，請確認金鑰檔案長度是否大於或等於2048\n"

	#4.2 - 1.1.19
	tmpItem="4.2"
	tmpIndex=1
	tmpPKI_list=""
	for i in range(len(tmpPKI[0])):
		tmpPKI_list=tmpPKI_list+tmpPKI[0][i]
	del Directory[tmpItem][tmpIndex]["audit output"]
	Directory[tmpItem][tmpIndex]['audit output']=[""]
	Directory[tmpItem][tmpIndex]["audit output"][0]="pki資料夾之檔案擁有者權限設定如下：\n"+tmpPKI_list
	#4.2 - 1.1.20
	tmpItem="4.2"
	tmpIndex=2
	tmpPKI_list=""
	for i in range(len(tmpPKI[1])):
		tmpPKI_list=tmpPKI_list+tmpPKI[1][i]
	del Directory[tmpItem][tmpIndex]["audit output"]
	Directory[tmpItem][tmpIndex]['audit output']=[""]
	Directory[tmpItem][tmpIndex]["audit output"][0]="pki資料夾之憑證檔案權限設定如下：\n"+tmpPKI_list
	#4.2 - 1.1.21
	tmpItem="4.2"
	tmpIndex=3
	tmpPKI_list=""
	for i in range(len(tmpPKI[2])):
		tmpPKI_list=tmpPKI_list+tmpPKI[2][i]
	del Directory[tmpItem][tmpIndex]["audit output"]
	Directory[tmpItem][tmpIndex]['audit output']=[""]
	Directory[tmpItem][tmpIndex]["audit output"][0]="pki資料夾之金鑰檔案權限設定如下：\n"+tmpPKI_list

	#4.8 - 1.1.1
	tmpItem="4.8"
	tmpIndex=1
	Directory[tmpItem][tmpIndex]["audit output"][0]="kube-apiserver.yaml檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#4.8 - 1.1.2
	tmpItem="4.8"
	tmpIndex=2
	Directory[tmpItem][tmpIndex]["audit output"][0]="kube-apiserver.yaml擁有者檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#4.8 - 1.1.3
	tmpItem="4.8"
	tmpIndex=3
	Directory[tmpItem][tmpIndex]["audit output"][0]="kube-controller-manager.yaml檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#4.8 - 1.1.4
	tmpItem="4.8"
	tmpIndex=4
	Directory[tmpItem][tmpIndex]["audit output"][0]="kube-controller-manager.yaml擁有者檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#4.8 - 1.1.6
	tmpItem="4.8"
	tmpIndex=5
	Directory[tmpItem][tmpIndex]["audit output"][0]="kube-scheduler.yaml擁有者檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#4.8 - 1.1.7
	tmpItem="4.8"
	tmpIndex=6
	Directory[tmpItem][tmpIndex]["audit output"][0]="etcd.yaml檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]
	#4.8 - 1.1.8
	tmpItem="4.8"
	tmpIndex=7
	Directory[tmpItem][tmpIndex]["audit output"][0]="etcd.yaml擁有者檔案權限設置為： "+Directory[tmpItem][tmpIndex]["audit output"][0]

	#4.11 - 1.2.22
	tmpItem="4.11"
	tmpIndex=1
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter="--audit-log-maxage"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定, 保留日誌天數參數未設定\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"保留日誌天數參數設定為"+tmpActualConfig+"\n"

	#4.11 - 1.2.23
	tmpItem="4.11"
	tmpIndex=2
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter="--audit-log-maxbackup"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定, 保留日誌檔案數參數未設定\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"保留日誌檔案數參數設定為"+tmpActualConfig+"\n\n"

	#4.11 - 1.2.24
	tmpItem="4.11"
	tmpIndex=3
	tmpline=Directory[tmpItem][tmpIndex]["audit output"][0]
	tmpParameter="--audit-log-maxsize"
	if tmpline.find(tmpParameter)==-1:
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"參數未設定, 保留日誌檔案大小參數未設定\n"
	else:
		tmpActualConfig=getValue(tmpline,tmpParameter)
		Directory[tmpItem][tmpIndex]["audit output"][0]=tmpParameter+"保留日誌檔案大小參數設定為"+tmpActualConfig+"\n"

	#4.11 - log permission
	Directory["4.11"]=Directory["4.11"]+[{}]
	Directory["4.11"][4]["CISID"]="1.2.21"
	Directory["4.11"][4]["CISResult"]=Directory["2.4"][1]["CISResult"]
	Directory["4.11"][4]["audit output"]=[""]
	Directory["4.11"][4]["audit output"][0]=Directory["2.4"][1]["audit output"][0]
	if Directory["4.11"][4]["CISResult"]=="FAIL":
		Directory["4.11"][0]["Final Result"]="FAIL"

	tmpline=Directory["4.3"][1]["audit output"]
	if tmpline.find("Signature Algorithm: sha")!=-1:
	    tmplist=tmpline.split("\n")
	    initalPass=1
	    for i in range(len(tmplist)-1):
	        if int(tmplist[i].split("Signature Algorithm: sha")[1].split("With")[0])<256:
	            initalPass=0
	    if initalPass==1:
	    	Directory["4.3"][1]["CISResult"]="PASS"
	    else:
	    	Directory["4.3"][1]["CISResult"]="FAIL"
	else:
		Directory["4.3"][1]["comment"]="未發現金鑰檔案，請確認金鑰加密演算法大於或等於sha256\n"

	#4.7 - 5.7.1
	tmpline=Directory["4.7"][1]["audit output"]
	if tmpline:
		initalPass=1
		for i in range(2,len(tmpline)-1):
			if tmpline[i].split(" ")[0]=="default":
				initalPass=0
			if tmpline[i] == "===namespaces list===\n":
				break
		if initalPass==1:
			Directory["4.7"][1]["CISResult"]="PASS"
			Directory["4.7"][1]["audit output"]=["已確認未使用default namespaces\n"]+tmpline
		else:
			Directory["4.7"][1]["CISResult"]="FAIL"
			Directory["4.7"][1]["audit output"]=["已確認使用default namespaces\n"]+tmpline
	else:
		Directory["4.7"][1]["audit output"]="未發現Pod資訊，請確認未使用名稱為『default』之namespace\n"

	#4.13 - 5.3.2
	tmpItem="4.13"
	tmpIndex=2
	tmpline=Directory[tmpItem][tmpIndex]["audit output"]
	del Directory[tmpItem][tmpIndex]["audit output"]
	Directory[tmpItem][tmpIndex]["audit output"]=[""]
	if tmpline:
	    if tmpline[0]=="Networkpolicy_Name\n" and tmpline[1]=="NAME              STATUS   AGE\n":
	    	Directory[tmpItem][tmpIndex]["CISResult"]="FAIL"
	    	Directory[tmpItem][tmpIndex]["audit output"][0]=["已確認Network policy未設定：\n"]+tmpline
	    else:
	    	Directory[tmpItem][tmpIndex]["audit output"][0]=["Network policy設定如下，請確認已妥適設定Network policy：\n"]+tmpline
	else:
		Directory[tmpItem][tmpIndex]["comment"]="未發現Pod資訊，請確認已妥適設定Network policy"

	#5.1 - 1.2.9
	tmpline=Directory["5.1"][1]["audit output"][0]
	if enableAdmissionPlugins.find("EventRateLimit")==-1:
		Directory["5.1"][1]["CISResult"]="FAIL"
		Directory["5.1"][1]["audit output"][0]="enable-Admission-Plugins之EventRateLimit參數未設定\n"
	elif tmpline.find("--admission-control-config-file")==-1:
		Directory["5.1"][1]["CISResult"]="FAIL"
		Directory["5.1"][1]["audit output"][0]="admission-control-config-file參數未設定\n"
	else:
		Directory["5.1"][1]["CISResult"]="Manual"
		Directory["5.1"][1]["audit output"][0]="admission-control-config-file參數設定為"+getValue(tmpline,--admission-control-config-file)+", 請確認EventRateLimit設定是否符合系統需求\n"
	
	tmpline=Directory["6.1"][1]["audit output"]
	Directory["6.1"][1]["audit output"]=["請確認以下設定是否符合每個pod設定專屬service account，及避免使用default namespace"]+tmpline

	return Directory
