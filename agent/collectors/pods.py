from kubernetes import client
from datetime import datetime, timezone

def collect_pods(cluster_id):
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces().items

    for p in pods:
        yield (
            cluster_id,
            p.metadata.namespace,
            p.metadata.name,
            p.status.phase,
            sum(c.restart_count for c in p.status.container_statuses or []),
            datetime.now(timezone.utc)
        )
