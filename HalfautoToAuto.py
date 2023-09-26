import string

def getValue(line,parameter):
	return line.split(parameter)[1].split(' ')[0]

def half_auto_To_auto(Directory):
	if Directory["1.2"][1]["audit output"][0].find("--anonymous-auth=true")==-1:
		Directory["1.2"][1]["CISResult"]="PASS"

	if Directory["1.3"][1]["audit output"][0].find("--encryption-provider-config")==-1:
		Directory["1.3"][1]["CISResult"]="FAIL"
	else:
		Directory["1.3"][1]["comment"]="請確認encryption-provider-config設定檔案是否符合系統需求"

	if Directory["1.5"][1]["audit output"][0].find("--request-timeout")==-1:
		Directory["1.5"][1]["CISResult"]="PASS"
	else:
		setValue=60
		setValue=int(getValue(Directory["1.5"][1]["audit output"][0],"--request-timeout="))
		if setValue>=60:
			Directory["1.5"][1]["CISResult"]="PASS"
		else:
			Directory["1.5"][1]["comment"]="請確認request-timeout設定是否符合系統需求"

	if Directory["3.1"][1]["audit output"][0].find("--audit-policy-file")==-1:
		Directory["3.1"][1]["CISResult"]="FAIL"
	else:
		Directory["3.1"][1]["comment"]="請確認audit-policy-file設定是否符合系統需求"

	tmpline=Directory["4.1"][1]["audit output"]
	if tmpline.find("RSA Private-Key: (")!=-1:
	    tmplist=tmpline.split("\n")
	    initalPass=1
	    for i in range(len(tmplist)-1):
	        if int(tmplist[i].split("Private-Key: (")[1].split(" bit")[0])<2048:
	            initalPass=0
	    if initalPass==1:
	    	Directory["4.1"][1]["CISResult"]="PASS"
	    else:
	    	Directory["4.1"][1]["CISResult"]="FAIL"
	else:
		Directory["4.1"][1]["comment"]="未發現金鑰檔案，請確認金鑰檔案長度是否大於或等於2048"

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
		Directory["4.3"][1]["comment"]="未發現金鑰檔案，請確認金鑰加密演算法大於或等於sha256"

	tmpline=Directory["4.7"][1]["audit output"]
	if tmpline:
	    initalPass=1
	    for i in range(2,len(tmpline)-1):
	        if tmpline[i].split(" ")[0]=="default":
	            initalPass=0
	    if initalPass==1:
	    	Directory["4.7"][1]["CISResult"]="PASS"
	    else:
	    	Directory["4.7"][1]["CISResult"]="FAIL"
	else:
		Directory["4.7"][1]["comment"]="未發現Pod資訊，請確認未使用名稱為『default』之namespace"

	tmpline=Directory["4.13"][1]["audit output"]
	if tmpline:
	    if tmpline[0]=="Networkpolicy_Name\n" and tmpline[1]=="NAME                     STATUS   AGE\n":
	    	Directory["4.13"][1]["CISResult"]="FAIL"
	    else:
	    	Directory["4.13"][1]["comment"]="請確認已妥適設定Networkpolicy"
	else:
		Directory["4.13"][1]["comment"]="未發現Pod資訊，請確認已妥適設定Networkpolicy"

	if Directory["5.1"][1]["audit output"][0].find("--admission-control-config-file")==-1 or Directory["5.1"][1]["audit output"][0].find("EventRateLimit")==-1:
		Directory["5.1"][1]["CISResult"]="FAIL"
	else:
		Directory["5.1"][1]["comment"]="請確認EventRateLimit設定是否符合系統需求"

	tmpline=Directory["6.1"][1]["audit output"]
	if tmpline and len(tmpline)>1:
	    if tmpline[1].split(' ')[0]=="service/kubernetes" and len(tmpline)==2:
	    	Directory["6.1"][1]["CISResult"]="FAIL"
	    else:
	    	Directory["6.1"][1]["comment"]="請確認對每個pod設定專屬service account"
	else:
		Directory["6.1"][1]["comment"]="未發現service account資訊，請確認已妥適設定"

	return Directory
