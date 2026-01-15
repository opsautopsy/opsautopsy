from datetime import timedelta

def detect_change_related_incident(timeline, window_minutes=10):
    deployments = [
        t for t in timeline if t["type"] == "deployment"
    ]

    events = [
        t for t in timeline if t["type"] == "event"
    ]

    for d in deployments:
        for e in events:
            if e["time"] > d["time"] and e["time"] <= d["time"] + timedelta(minutes=window_minutes):
                return True, d["name"]

    return False, None
