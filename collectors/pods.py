from kubernetes import client, config
from datetime import timezone


def collect_pods(namespace, start_time=None):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    pods = []
    raw_pods = v1.list_namespaced_pod(namespace).items

    for p in raw_pods:
        if not p.status.start_time:
            continue

        pod_time = p.status.start_time.astimezone(timezone.utc)

        if start_time and pod_time < start_time:
            continue

        pods.append({
            "time": pod_time,
            "type": "pod",
            "namespace": namespace,
            "name": p.metadata.name,
            "status": p.status.phase,
            "restarts": sum(
                cs.restart_count for cs in (p.status.container_statuses or [])
            )
        })

    return pods
