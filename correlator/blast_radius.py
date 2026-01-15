def calculate_blast_radius(timeline):
    pods = set()
    deployments = set()

    for item in timeline:
        if item["type"] == "pod":
            pods.add(item["name"])

        if item["type"] == "event":
            pods.add(item["object"])

        if item["type"] == "deployment":
            deployments.add(item["name"])

    return {
        "affected_pods": len(pods),
        "affected_deployments": len(deployments)
    }
