import argparse
from datetime import datetime, timedelta, timezone

from collectors.events import collect_events
from collectors.pods import collect_pods
from collectors.deployments import collect_deployments
from correlator.timeline import build_timeline
from output.formatter import print_timeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="OpsAutopsy – Kubernetes Incident Timeline"
    )

    parser.add_argument(
        "--namespace",
        default="default",
        help="Kubernetes namespace (default: default)"
    )

    parser.add_argument(
        "--since",
        help="Start time (ISO format: YYYY-MM-DDTHH:MM)"
    )

    parser.add_argument(
        "--last-minutes",
        type=int,
        help="Show incidents from last N minutes"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # -------------------------------
    # Time filtering logic (UTC aware)
    # -------------------------------
    start_time = None

    if args.since:
        # Convert ISO string to UTC-aware datetime
        start_time = datetime.fromisoformat(args.since)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

    elif args.last_minutes:
        start_time = datetime.now(timezone.utc) - timedelta(
            minutes=args.last_minutes
        )

    # -------------------------------
    # Collect Kubernetes data
    # -------------------------------
    events = collect_events(args.namespace, start_time)
    pods = collect_pods(args.namespace, start_time)
    deployments = collect_deployments(args.namespace, start_time)

    # -------------------------------
    # Build & print timeline
    # -------------------------------
    timeline = build_timeline(events, pods, deployments)
    print_timeline(timeline)


if __name__ == "__main__":
    main()
