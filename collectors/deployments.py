from kubernetes import client, config
from datetime import timezone


def collect_deployments(namespace, start_time=None):
    config.load_kube_config()
    apps = client.AppsV1Api()

    deployments = []
    raw_deployments = apps.list_namespaced_deployment(namespace).items

    for d in raw_deployments:
        created_time = d.metadata.creation_timestamp.astimezone(timezone.utc)

        if start_time and created_time < start_time:
            continue

        deployments.append({
            "time": created_time,
            "type": "deployment",
            "namespace": namespace,
            "name": d.metadata.name,
            "image": d.spec.template.spec.containers[0].image,
            "replicas": d.spec.replicas
        })

    return deployments
