import argparse
import sys

from opsautopsy.analyze import run_analyze
from opsautopsy.config import set_db_url, get_db_url


def main():
    parser = argparse.ArgumentParser(
        prog="opsautopsy",
        description=(
            "OpsAutopsy – Kubernetes Post-Incident Forensics CLI\n\n"
            "OpsAutopsy reconstructs incident timelines by correlating\n"
            "Kubernetes events across clusters using historical data\n"
            "stored in PostgreSQL."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # 🔹 GLOBAL EPILOG
    parser.epilog = (
        "Common examples:\n"
        "  opsautopsy analyze --last-minutes 15\n"
        "  opsautopsy analyze --namespace payments --last-minutes 60\n"
        "  opsautopsy analyze --clusters prod-eu,prod-us --since 2026-01-15T16:00\n\n"
        "Run 'opsautopsy <command> --help' for detailed options."
        "Database configuration:\n"
        "  opsautopsy config set-db postgresql://user:pass@localhost:5432/opsautopsy\n\n"
        "Run 'opsautopsy <command> --help' for detailed options."
    )

    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command",
        metavar="{analyze,config}",
        required=True,
    )

    # =========================================================
    # analyze command
    # =========================================================
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze incidents from collected Kubernetes events",
        description=(
            "Analyze Kubernetes incidents by querying historical\n"
            "events stored by OpsAutopsy agents and reconstructing\n"
            "a human-readable incident timeline."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    analyze_parser.add_argument(
        "--clusters",
        help=(
            "Comma-separated cluster IDs to analyze\n"
            "Example: prod-eu,prod-us\n"
            "Default: all clusters"
        ),
        default=None,
    )

    analyze_parser.add_argument(
        "--namespace",
        help=(
            "Kubernetes namespace filter\n"
            "Example: payments"
        ),
        default=None,
    )

    analyze_parser.add_argument(
        "--since",
        help=(
            "Start time (UTC, ISO format)\n"
            "Example: 2026-01-15T16:00"
        ),
        default=None,
    )

    analyze_parser.add_argument(
        "--last-minutes",
        type=int,
        help=(
            "Analyze incidents from the last N minutes\n"
            "Example: --last-minutes 30"
        ),
        default=None,
    )

    analyze_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help=(
            "Output format\n"
            "text (default) – human-readable report\n"
            "json            – machine-readable output"
        ),
    )

    analyze_parser.epilog = (
        "Examples:\n"
        "  opsautopsy analyze --last-minutes 15\n"
        "  opsautopsy analyze --namespace payments --last-minutes 60\n"
        "  opsautopsy analyze --clusters prod-eu,prod-us --since 2026-01-15T16:00\n"
        "  opsautopsy analyze --namespace opsautopsy --last-minutes 30 --format json\n"
    )

    # =========================================================
    # config command
    # =========================================================
    config_parser = subparsers.add_parser(
        "config",
        help="Configure OpsAutopsy settings",
        description=(
            "Configure local OpsAutopsy CLI settings.\n\n"
            "This configuration is used only by the analyzer CLI.\n"
            "Agents running in Kubernetes should continue using\n"
            "environment variables or Kubernetes Secrets."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    config_subparsers = config_parser.add_subparsers(
        dest="config_command",
        metavar="{set-db,show}",
        required=True,
    )

    # ---- config set-db
    set_db_parser = config_subparsers.add_parser(
        "set-db",
        help="Set PostgreSQL database URL",
        description=(
            "Set the PostgreSQL database URL used by the analyzer.\n\n"
            "The value is stored locally in:\n"
            "  ~/.opsautopsy/config.yaml"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    set_db_parser.add_argument(
        "url",
        help=(
            "PostgreSQL connection URL\n"
            "Example:\n"
            "  postgresql://user:password@localhost:5432/opsautopsy"
        ),
    )

    # ---- config show
    show_parser = config_subparsers.add_parser(
        "show",
        help="Show current configuration",
        description="Display the current local OpsAutopsy configuration.",
    )

    # =========================================================
    # EXECUTION
    # =========================================================
    args = parser.parse_args()

    if args.command == "analyze":
        run_analyze(args)

    elif args.command == "config":
        if args.config_command == "set-db":
            set_db_url(args.url)
            print("✔ Database URL saved successfully")

        elif args.config_command == "show":
            db_url = get_db_url()
            print("OpsAutopsy Configuration")
            print("------------------------")
            print(f"Database URL : {db_url if db_url else 'NOT SET'}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
