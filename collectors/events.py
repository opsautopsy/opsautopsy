from kubernetes import client, config
from datetime import timezone


def collect_events(namespace, start_time=None):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    events = []
    raw_events = v1.list_namespaced_event(namespace).items

    for e in raw_events:
        if not e.last_timestamp:
            continue

        event_time = e.last_timestamp.astimezone(timezone.utc)

        if start_time and event_time < start_time:
            continue

        events.append({
            "time": event_time,
            "type": "event",
            "namespace": namespace,
            "object": e.involved_object.name,
            "reason": e.reason,
            "message": e.message
        })

    return events
