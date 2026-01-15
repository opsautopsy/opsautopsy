from collections import defaultdict
from correlator.summary import build_incident_summary


def print_summary(summary):
    print("\n🚨 INCIDENT SUMMARY")
    print("------------------")

    print("Detected Issues:")
    for issue in summary["issues"]:
        print(f"  - {issue}")

    print(f"\nAffected Pods    : {summary['blast_radius']['affected_pods']}")
    print(f"Affected Deploys : {summary['blast_radius']['affected_deployments']}")

    if summary["change_related"]:
        print(f"Change Related   : YES (Deployment: {summary['related_deployment']})")
    else:
        print("Change Related   : NO")



def print_timeline(timeline):
    # -------------------------------------------------
    # 1. Build & print incident summary (TOP SECTION)
    # -------------------------------------------------
    summary = build_incident_summary(timeline)
    print_summary(summary)

    print("\n🧠 OPSAUTOPSY INCIDENT TIMELINE\n")

    # -------------------------------------------------
    # 2. Group by namespace → pod/workload
    # -------------------------------------------------
    grouped = defaultdict(lambda: defaultdict(list))

    for item in timeline:
        namespace = item.get("namespace", "unknown")

        if item["type"] == "deployment":
            key = f"DEPLOYMENT::{item['name']}"
        elif item["type"] == "pod":
            key = f"POD::{item['name']}"
        else:  # event
            key = f"POD::{item['object']}"

        grouped[namespace][key].append(item)

    # -------------------------------------------------
    # 3. Print grouped timeline
    # -------------------------------------------------
    for namespace, objects in grouped.items():
        print(f"\n📦 Namespace: {namespace}")
        print("=" * (14 + len(namespace)))

        for obj, items in objects.items():
            print(f"\n🔹 {obj}")
            print("-" * (len(obj) + 4))

            # Sort timeline within each pod/workload
            items.sort(key=lambda x: x["time"])

            for i in items:
                time = i["time"].strftime("%Y-%m-%d %H:%M:%S")

                if i["type"] == "event":
                    print(f"{time} | EVENT | {i['reason']}")
                elif i["type"] == "pod":
                    print(
                        f"{time} | POD   | status={i['status']} "
                        f"restarts={i['restarts']}"
                    )
                elif i["type"] == "deployment":
                    print(
                        f"{time} | DEPLOYMENT | image={i['image']}"
                    )

    print("\n--- END OF OPSAUTOPSY ---\n")
