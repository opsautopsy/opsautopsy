from collections import defaultdict

def build_incidents(events):
    incidents = defaultdict(list)

    for e in events:
        key = (e["name"], e["reason"])
        incidents[key].append(e)

    return incidents
