from kubernetes import client

def collect_nodes():
    v1 = client.CoreV1Api()
    return [n.metadata.name for n in v1.list_node().items]
