from correlator.root_cause import detect_issue_types
from correlator.blast_radius import calculate_blast_radius
from correlator.change_detection import detect_change_related_incident


def build_incident_summary(timeline):
    issues = detect_issue_types(timeline)
    blast = calculate_blast_radius(timeline)
    change_related, deployment = detect_change_related_incident(timeline)

    return {
        "issues": issues,
        "blast_radius": blast,
        "change_related": change_related,
        "related_deployment": deployment
    }
