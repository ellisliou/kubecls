import json
import yaml
import subprocess
from datetime import datetime, timezone, timedelta
import requests
import glob
import jwt

clair_log = open('clair_log.txt', 'w')

def clair_log_close():
	clair_log.close()

def checkClair(clair_IP):
	Pod_outputDirectory={}
	clair_outputDirectory={}

	file = open("k8s_pods.yaml")
	file = yaml.load(file, Loader=yaml.FullLoader)

	if not file: #k8s_pods
		print("Pods is empty!\n")
		clair_log.write("Pods is empty!\n")
	else:
		print("Total items: ",len(file["items"]),"\n")
		clair_log.write("Total items: "+str(len(file["items"]))+"\n")
		tempList=[]
		for i in range(len(file["items"])):
			temp_item=file["items"][i]
			print('item '+str(i)+':')
			print(temp_item["metadata"]["name"])
			print(temp_item["spec"]["containers"][0]["image"])
			print(temp_item["spec"]["containers"][0]["imagePullPolicy"],"\n")

			imageName=temp_item["spec"]["containers"][0]["image"]
			manifestOutput=subprocess.check_output(["./clairctl-linux-amd64","manifest",imageName])
			scanStatus=0
			try:
				manifestJson=json.loads(manifestOutput)
				imageHashID=manifestJson["hash"]
				print("Image hash: "+imageHashID)
				clair_log.write("Image hash: "+imageHashID+"\n")
			except:
				print("Unknown image name or tag name\n")
				clair_log.write("Unknown image name or tag name\n")
				scanStatus=1 #abnormal status

			try:
				subprocess.call(["./clairctl-linux-amd64","-D","-c","/root/clair-v4.7.2/local-dev/clair/config.yaml","report",imageName])
				print("Image scanning is completed!")
				clair_log.write("Image scanning is completed!\n")
			except:
				print("Clair service is unavailable\n")
				clair_log.write("Clair service is unavailable\n")
				scanStatus=1 #abnormal status

			if(scanStatus==0):
				clair_log.write("Scan start:"+imageName+","+imageHashID+","+str(datetime.now())+"\n")

				scanResultUrl="http://"+clair_IP+":6060/matcher/api/v1/vulnerability_report/"+imageHashID
				responseStatuses = {200: "Website Available",301: "Permanent Redirect",302: "Temporary Redirect",404: "Not Found",500: "Internal Server Error",503: "Service Unavailable"}
				jwttoken=jwt.encode({"iss": "clairctl","exp": datetime.now(tz=timezone.utc) + timedelta(seconds=60),"nbf": datetime.now(tz=timezone.utc) - timedelta(seconds=120),"iat": datetime.now(tz=timezone.utc)},"secret",algorithm="HS256")
				print(jwttoken)
				headers={"Authorization":"Bearer "+jwttoken}

				try:
					web_response = requests.get(scanResultUrl,headers=headers,timeout=30)
					print(scanResultUrl, responseStatuses[web_response.status_code],"\n\n")
					clair_log.write(scanResultUrl+"\n"+responseStatuses[web_response.status_code]+"\n\n")
					#print(web_response.text)
				except:
					print("Connection error\n")
					clair_log.write("Connection error\n")
			findResult=0
			for k in range(len(tempList)):
				if(imageHashID==tempList[k]):
					findResult=1
			if(findResult==0):
				tempList.append(imageHashID)
				clair_outputDirectory[imageHashID]=json.loads(web_response.text)
				Pod_outputDirectory[imageHashID]={"image_name":temp_item["spec"]["containers"][0]["image"],"pod_info":[{"pod_name":temp_item["metadata"]["name"],"imagePullPolicy":temp_item["spec"]["containers"][0]["imagePullPolicy"]}]}
			else:
				Pod_outputDirectory[imageHashID]["pod_info"]=Pod_outputDirectory[imageHashID]["pod_info"]+[{"pod_name":temp_item["metadata"]["name"],"imagePullPolicy":temp_item["spec"]["containers"][0]["imagePullPolicy"]}]
			#Pod_outputDirectory[i]={"pod_name":temp_item["metadata"]["name"],"image_name":temp_item["spec"]["containers"][0]["image"],"imagePullPolicy":temp_item["spec"]["containers"][0]["imagePullPolicy"],"image_Hash_ID":imageHashID}
		with open("pod_info.json", "w") as outfile:
			json.dump(Pod_outputDirectory, outfile)
		with open("clair_result.json", "w") as outfile:
			json.dump(clair_outputDirectory, outfile)