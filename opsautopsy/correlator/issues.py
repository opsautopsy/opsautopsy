def detect_issues(events):
    issues = set()
    for e in events:
        if e["reason"] == "FailedScheduling":
            issues.add("CAPACITY")
        if "BackOff" in e["reason"]:
            issues.add("CRASH_LOOP")
    return list(issues)
