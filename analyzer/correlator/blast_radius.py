def blast_radius(events):
    pods = {e["object_name"] for e in events}
    return len(pods)
