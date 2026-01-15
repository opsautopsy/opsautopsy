from opsautopsy.correlator.timeline import build_timeline
from opsautopsy.output.formatter import print_report
from opsautopsy.output.json_exporter import export_json

from datetime import datetime, timedelta, timezone


def run_analyze(args):
    if args.since:
        start_time = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
    elif args.last_minutes:
        start_time = datetime.now(timezone.utc) - timedelta(minutes=args.last_minutes)
    else:
        start_time = None

    clusters = args.clusters.split(",") if args.clusters else None

    timeline = build_timeline(
        clusters=clusters,
        namespace=args.namespace,
        start_time=start_time,
    )

    if args.format == "json":
        export_json(timeline)
    else:
        print_report(timeline)
