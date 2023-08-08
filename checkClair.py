import json
import yaml
import subprocess
import datetime
import requests
import glob

def checkClair(clair_IP):
	Pod_outputDirectory={}
	clair_outputDirectory={}

	file = open("k8s_pods.yaml")
	file = yaml.load(file, Loader=yaml.FullLoader)
	f_exec_log = open('execlog.txt', 'a')

	if file is None: #k8s_pods
		print("Pods is empty!\n")
	else:
		print("Total items: ",len(file["items"]),"\n")
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
			except:
				print("Unknown image name or tag name\n")
				scanStatus=1 #abnormal status

			try:
				subprocess.call(["./clairctl-linux-amd64","-D","report",imageName])
				print("Image scanning is completed!")
			except:
				print("Clair service is unavailable\n")
				scanStatus=1 #abnormal status

			if(scanStatus==0):
			    f_exec_log.write("Scan start:"+imageName+","+imageHashID+","+str(datetime.datetime.now())+"\n")

			    #print(scanOutput)
			    #get json file of scan result
			    scanResultUrl="http://"+clair_IP+":6060/matcher/api/v1/vulnerability_report/"+imageHashID
			    responseStatuses = {200: "Website Available",301: "Permanent Redirect",302: "Temporary Redirect",404: "Not Found",500: "Internal Server Error",503: "Service Unavailable"}

			    try:
			        web_response = requests.get(scanResultUrl,timeout=3)
			        print(scanResultUrl, responseStatuses[web_response.status_code],"\n\n")
			        #print(web_response.text)
			    except:
			        print("Connection error\n")
			findResult=0
			for k in range(len(tempList)):
				if(imageHashID==tempList[k]):
					findResult=1
			if(findResult==0):
				clair_outputDirectory[imageHashID]=json.loads(web_response.text)
			Pod_outputDirectory[i]={"pod_name":temp_item["metadata"]["name"],"image_name":temp_item["spec"]["containers"][0]["image"],"imagePullPolicy":temp_item["spec"]["containers"][0]["imagePullPolicy"],"image_Hash_ID":imageHashID}
		with open("pod_info.json", "w") as outfile:
			json.dump(Pod_outputDirectory, outfile)
		with open("clair_result.json", "w") as outfile:
			json.dump(clair_outputDirectory, outfile)