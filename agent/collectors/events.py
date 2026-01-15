from kubernetes import client, watch
from datetime import timezone

def stream_events(cluster_id):
    v1 = client.CoreV1Api()
    w = watch.Watch()

    for event in w.stream(v1.list_event_for_all_namespaces):
        obj = event.get("object")

        if not obj or not obj.last_timestamp:
            continue

        yield (
            cluster_id,
            obj.metadata.namespace,
            obj.involved_object.kind,
            obj.involved_object.name,
            obj.reason,
            obj.message,
            obj.last_timestamp.replace(tzinfo=timezone.utc)
        )
