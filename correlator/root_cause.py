def detect_issue_types(timeline):
    """
    Detect ALL issue types present in the incident window.
    Returns a sorted list of issue labels.
    """

    issues = set()

    for item in timeline:
        if item["type"] != "event":
            continue

        reason = item["reason"]

        # Image / artifact issues
        if reason in ["ErrImagePull", "ImagePullBackOff", "Failed"]:
            issues.add("IMAGE_PULL_FAILURE")

        # Memory / OOM issues
        if "OOM" in reason:
            issues.add("MEMORY_OOM")

        # Scheduling / capacity issues
        if reason == "FailedScheduling":
            issues.add("CAPACITY_SCHEDULING")

        # Crash loop / runtime issues
        if reason == "BackOff":
            issues.add("CRASH_LOOP")

    if not issues:
        issues.add("NO_FAILURE_DETECTED")

    return sorted(issues)
