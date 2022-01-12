from kubernetes import client,config
config.kube_config.load_kube_config(config_file="/home/k/kubeconfig.yaml")

#get API CoreV1Api object
v1 = client.CoreV1Api()

print("=====list namespaces====")
for ns in v1.list_namespace().items:
  print(ns.metadata.name)

print("\n\n=====list all services====")
ret = v1.list_service_for_all_namespaces(watch=False)
for i in ret.items:
  print("%s \t%s \t%s \t%s \t%s \n" % (i.kind,i.metadata.namespace,i.metadata.name,i.spec.cluster_ip,i.spec.ports ))

print("\n\n=====list all pods====")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
  print("%s\t%s" % (i.status.pod_ip,i.metadata.name))

print("\n\n=====list all deploy====")
ret = v1.list_deployment_for_all_namespaces(watch=False)
for i in ret.items:
  print("%s\t%s" % (i.status.pod_ip,i.metadata.name))
