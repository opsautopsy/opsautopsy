# OpsAutopsy

**Cloud-agnostic, multi-cluster Kubernetes incident forensics engine**

OpsAutopsy reconstructs what happened during outages by correlating Kubernetes events, workload state, and change signals across clusters into clear, time-ordered incident reports.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.24+-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)

---

## The Problem

When incidents occur, your team scrambles to answer:

- **What happened first?** — Alert floods make root cause unclear
- **What changed?** — Deployments, configs, and infrastructure changes are scattered
- **Why did it fail?** — Correlation between events is lost in noise
- **How wide was the impact?** — Blast radius spans multiple clusters
- **Did this cascade?** — Cross-cluster failures are invisible

**Most observability tools show signals. OpsAutopsy explains incidents.**

---

## The Solution

OpsAutopsy is purpose-built for **post-incident analysis**, not real-time monitoring.

### Key Capabilities

**🔍 Multi-Cluster Incident Reconstruction**  
Correlate events across all your Kubernetes clusters in a single timeline

**🕐 Time-Travel Debugging**  
Query historical cluster state even after Kubernetes garbage-collects events

**🎯 Root Cause Classification**  
Automatically detect issue types: ImagePullBackOff, CrashLoop, OOMKilled, capacity constraints

**📊 Blast Radius Analysis**  
Understand incident scope: affected pods, deployments, namespaces, and clusters

**🔗 Change Correlation**  
Link incidents to deployments, config changes, and infrastructure events

**📝 Human-Readable Reports**  
Get clear incident narratives, not just raw data dumps

---

## Architecture

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Cluster A   │   │  Cluster B   │   │  Cluster C   │
│              │   │              │   │              │
│ OpsAutopsy   │   │ OpsAutopsy   │   │ OpsAutopsy   │
│ Agent        │   │ Agent        │   │ Agent        │
│ (DaemonSet)  │   │ (DaemonSet)  │   │ (DaemonSet)  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────┬───────┴──────────┬───────┘
                  ▼                  ▼
         ┌─────────────────────────────────┐
         │ Centralized PostgreSQL Database │
         │  (Events, State, Metadata)      │
         └────────────────┬────────────────┘
                          ▼
              ┌───────────────────────┐
              │ OpsAutopsy Analyzer   │
              │ (CLI - Stateless)     │
              └───────────────────────┘
```

### Components

#### 1. OpsAutopsy Agent (Per-Cluster)

Deployed as a **DaemonSet** for comprehensive node-level coverage.

**Responsibilities:**
- Watch Kubernetes Events API
- Observe Pod, Deployment, and Node state
- Normalize timestamps to UTC
- Tag all data with `cluster_id`
- Stream events to centralized storage

**Design Principles:**
- **Read-only:** Zero risk to cluster stability
- **Lightweight:** Minimal resource footprint
- **Safe:** No cluster state mutations

#### 2. Centralized Storage (PostgreSQL)

Kubernetes events are ephemeral (typically 1-hour TTL). OpsAutopsy provides durable incident memory.

**Why PostgreSQL?**
- Powerful time-series querying
- Native JSON support for flexible schemas
- Cross-cluster correlation via SQL joins
- Battle-tested reliability
- Simple operational model

**Core Schema:**

```sql
-- events table
cluster_id, namespace, object_kind, object_name, 
reason, message, event_time

-- workload_state table
cluster_id, namespace, workload_name, workload_type,
status, restart_count, observed_time
```

#### 3. OpsAutopsy Analyzer (CLI)

Stateless analysis engine that runs outside your clusters.

**Capabilities:**
- Query events across time windows and clusters
- Classify incident types automatically
- Calculate blast radius
- Correlate changes with failures
- Generate human-readable reports

**Example Usage:**

```bash
# Analyze recent incident across production clusters
opsautopsy analyze \
  --clusters prod-eu,prod-us \
  --namespace payments \
  --since 6h

# Investigate specific deployment
opsautopsy analyze \
  --deployment checkout-service \
  --from "2024-01-15T18:00:00Z" \
  --to "2024-01-15T19:00:00Z"

# Export structured data
opsautopsy analyze --since 12h --format json > incident.json
```

---

## Sample Output

### Incident Summary

```
═══════════════════════════════════════════════════
INCIDENT ANALYSIS: 2024-01-15 18:14 - 18:32 UTC
═══════════════════════════════════════════════════

Detected Issues:
  • IMAGE_PULL_FAILURE (ErrImagePull, ImagePullBackOff)
  • CRASH_LOOP (CrashLoopBackOff)
  • CAPACITY_SCHEDULING (Insufficient CPU/Memory)

Impact:
  Affected Pods        : 9
  Affected Deployments : 1
  Namespaces           : 2
  Clusters             : prod-eu, prod-us

Change Correlation: NO
  No deployments or config changes detected in 1h window
```

### Timeline

```
18:14:23 UTC | WARN | prod-eu    | kube-system | FailedScheduling
             | Node cpu-pressure-node: Insufficient cpu

18:15:01 UTC | ERROR| prod-us    | payments    | BackOff
             | crashloop-pod: Back-off restarting failed container

18:16:47 UTC | ERROR| prod-eu    | payments    | Failed
             | bad-image-pod: ErrImagePull (manifest unknown)

18:18:12 UTC | WARN | prod-eu    | payments    | Unhealthy
             | Readiness probe failed (3 consecutive failures)
```

---

## Design Philosophy

### Separation of Concerns

**Collection ≠ Analysis**  
Agents collect, analyzer interprets. Clean boundaries enable independent scaling.

### Read-Only by Design

Agents never mutate cluster state. Zero blast-radius risk during incidents.

### Cloud-Agnostic

Works with any Kubernetes distribution: EKS, GKE, AKS, on-prem, k3s, etc.

### Multi-Cluster First

Treats clusters as a dimension, not a boundary. Incidents don't respect cluster limits.

### Post-Incident Intelligence

Complements real-time monitoring. Starts when alerts fire and understanding matters most.

---

## What OpsAutopsy Is NOT

| ❌ OpsAutopsy is NOT | ✅ Use Instead |
|---------------------|---------------|
| Real-time monitoring | Prometheus, Datadog |
| Alerting platform | PagerDuty, Opsgenie |
| Metrics scraping | Prometheus, VictoriaMetrics |
| Dashboard tool | Grafana, Kibana |
| Log aggregation | Loki, ELK Stack |

> **OpsAutopsy starts after alerts fire, when understanding matters most.**

---

## Roadmap

### ✅ v1.0 (Current Scope)

- [x] DaemonSet-based agents
- [x] Centralized PostgreSQL storage
- [x] Multi-cluster event correlation
- [x] Incident classification engine
- [x] Blast radius detection
- [x] CLI-based analysis and reporting

### 🚧 Future Enhancements

- [ ] Web UI for incident exploration
- [ ] Slack/Teams integration for report delivery
- [ ] Change tracking (GitOps, Helm, ArgoCD)
- [ ] Capacity trend analysis
- [ ] Export to incident management platforms
- [ ] S3/GCS archival for long-term retention

---

## Quick Start

```bash
# Deploy agent to your cluster
kubectl apply -f https://github.com/yourorg/opsautopsy/releases/latest/agent.yaml

# Configure database connection
kubectl create secret generic opsautopsy-db \
  --from-literal=url=postgresql://user:pass@host:5432/opsautopsy

# Install CLI
brew install opsautopsy
# or
go install github.com/yourorg/opsautopsy/cmd/opsautopsy@latest

# Run your first analysis
opsautopsy analyze --since 1h
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details

---

## Support

- 📖 **Documentation:** [docs.opsautopsy.io](https://docs.opsautopsy.io)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourorg/opsautopsy/discussions)
- 🐛 **Issues:** [GitHub Issues](https://github.com/yourorg/opsautopsy/issues)

---

**Built with ❤️ for SREs who deserve better incident post-mortems**