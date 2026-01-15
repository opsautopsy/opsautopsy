def build_timeline(events, pods, deployments):
    timeline = []

    timeline.extend(events)
    timeline.extend(pods)
    timeline.extend(deployments)

    # Remove entries without time
    timeline = [t for t in timeline if t["time"]]

    timeline.sort(key=lambda x: x["time"])
    return timeline
