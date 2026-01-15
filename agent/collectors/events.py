from kubernetes import client, watch
from datetime import timezone

def stream_events(cluster_id):
    v1 = client.CoreV1Api()
    w = watch.Watch()

    for e in w.stream(v1.list_event_for_all_namespaces):
        yield (
            cluster_id,
            e.metadata.namespace,
            e.involved_object.kind,
            e.involved_object.name,
            e.reason,
            e.message,
            e.last_timestamp.replace(tzinfo=timezone.utc)
        )
