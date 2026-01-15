import argparse
from correlator.timeline import build_timeline
from output.formatter import print_report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clusters")
    parser.add_argument("--since")
    args = parser.parse_args()

    timeline = build_timeline(args.clusters, args.since)
    print_report(timeline)

if __name__ == "__main__":
    main()
